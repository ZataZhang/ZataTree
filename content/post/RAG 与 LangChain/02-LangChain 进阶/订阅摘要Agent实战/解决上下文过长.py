from datetime import datetime
import time
import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI
import os
# Mock logger for tutorial purposes
class MockLogger:
    def debug(self, msg): print(f"DEBUG: {msg}")
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logger = MockLogger()

# Define the output model
class SummaryResponse(BaseModel):
    content: List[str] = Field(default_factory=list, description="Content update summaries")
    key_points: List[str] = Field(default_factory=list, description="List of key points")
    url_list: List[List[str]] = Field(default_factory=list, description="URLs corresponding to each key point")
    word_count: int = Field(default=0, description="Total word count of content")
    generated_at: str = Field(default="", description="Generation timestamp")
    status: str = Field(default="success", description="Processing status")
    error_message: Optional[str] = Field(default=None, description="Error message if any")
    raw_response: Optional[str] = Field(default=None, description="Raw LLM response")


# Subscription Agent
class SubscriptionAgent:
    def __init__(self, max_retries=3, retry_delay=2, max_token_limit=30000):
        logger.debug("Initializing SubscriptionAgent")
        self.max_token_limit = max_token_limit
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        logger.info(f"Agent parameters: max_retries={max_retries}, retry_delay={retry_delay}, max_token_limit={max_token_limit}")
        self.llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
)
        logger.debug("LLM initialized with qwen-plus model")
        self.parser = PydanticOutputParser(pydantic_object=SummaryResponse)
        logger.debug("PydanticOutputParser initialized with SummaryResponse model")

        # Define prompt template
        self.prompt_template = PromptTemplate(
            input_variables=["contentdiff"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""
            You are a subscription content expert. Summarize the following content differences:

            {contentdiff}

            ### Notes:
            - Ignore updates that are only time or data changes (return empty arrays).
            - Ensure content and key_points lists have a one-to-one correspondence.
            - url_list is a 2D array, each sublist contains URLs for the corresponding key point.

            ### Requirements:
            1. Provide content update summaries (content) as an array.
            2. Extract key points (key_points) for each content item.
            3. Extract URLs for each key point (url_list); return empty arrays if none.
            4. Calculate word count for content (Chinese/English characters only, no punctuation/spaces).
            5. Return results in Chinese if updates exist; otherwise, return empty arrays.
            6. Follow this JSON format:

            {format_instructions}
            """
        )
        logger.debug("Prompt template initialized")

        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=self.max_token_limit,
            return_messages=True
        )
        logger.debug("ConversationSummaryBufferMemory initialized")
        logger.info("SubscriptionAgent initialization completed")

    def extract_json(self, raw_content: str) -> str:
        logger.debug("Extracting JSON from raw content")
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        result = json_match.group(0) if json_match else raw_content
        logger.debug(f"JSON extraction {'successful' if json_match else 'failed, returning raw content'}")
        return result

    def generate_summary(self, contentdiff: str) -> SummaryResponse:
        logger.info("Starting generate_summary method")
        avg_token_per_char = 0.5
        estimated_tokens = len(contentdiff) * avg_token_per_char
        logger.info(f"Content length: {len(contentdiff)} chars, estimated tokens: {int(estimated_tokens)}")

        if estimated_tokens > self.max_token_limit:
            logger.info(f"Estimated tokens ({int(estimated_tokens)}) exceed limit ({self.max_token_limit}), using memory.")
            return self.generate_summary_with_memory(contentdiff)

        logger.debug("Starting summary generation...")
        retries = 0
        last_exception = None
        raw_response = None

        while retries < self.max_retries:
            try:
                logger.debug(f"Attempt {retries+1}/{self.max_retries} to generate summary")
                chain = self.prompt_template | self.llm
                logger.debug("Invoking LLM chain")
                raw_response = chain.invoke({"contentdiff": contentdiff})
                logger.debug("LLM response received")
                raw_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
                logger.debug("Extracting JSON content")
                json_content = self.extract_json(raw_content)
                logger.debug("Parsing response with PydanticOutputParser")
                response = self.parser.parse(json_content)
                logger.debug("Response parsed successfully")

                if not response.generated_at:
                    logger.debug("Setting generated_at timestamp")
                    response.generated_at = datetime.now().isoformat()
                if response.word_count == 0 and response.content:
                    logger.debug("Calculating word count")
                    response.word_count = len("".join(response.content).replace(" ", "").replace(",", "").replace(".", ""))
                    logger.debug(f"Word count calculated: {response.word_count}")
                response.raw_response = raw_content
                logger.debug("Summary generated successfully")
                logger.info(f"Summary generation completed with status: {response.status}")
                return response

            except Exception as e:
                logger.error(f"Summary generation failed: {e}")
                last_exception = e
                retries += 1
                if retries < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

        raw_content = raw_response.content if raw_response and hasattr(raw_response, 'content') else str(raw_response) if raw_response else "No response"
        logger.error(f"All retries failed: {str(last_exception)}")
        logger.info("Returning error response")
        return SummaryResponse(
            content=[],
            key_points=[],
            url_list=[],
            word_count=0,
            generated_at=datetime.now().isoformat(),
            status="error",
            error_message=f"Failed to parse SummaryResponse: {str(last_exception)}",
            raw_response=raw_content
        )

    def chunking_content(self, contentdiff: str) -> List[str]:
        logger.info("Starting content chunking")
        avg_token_per_char = 0.5
        estimated_tokens = len(contentdiff) * avg_token_per_char
        logger.info(f"Content length: {len(contentdiff)} chars, estimated tokens: {int(estimated_tokens)}")

        if estimated_tokens <= self.max_token_limit:
            logger.info("Content within token limit, no chunking needed")
            return [contentdiff]

        logger.debug("Content exceeds token limit, starting chunking process")
        chunks = []
        change_units = re.findall(r'""(?:Changed|Added|Deleted):.*?"",', contentdiff, re.DOTALL)
        logger.debug(f"Found {len(change_units)} change units in content")

        if not change_units:
            logger.debug("No change units found, chunking by character count")
            chars_per_chunk = int(self.max_token_limit / avg_token_per_char)
            logger.debug(f"Characters per chunk: {chars_per_chunk}")
            for i in range(0, len(contentdiff), chars_per_chunk):
                chunks.append(contentdiff[i:i+chars_per_chunk])
                logger.debug(f"Created chunk {len(chunks)} with {min(chars_per_chunk, len(contentdiff)-i)} characters")
        else:
            logger.debug("Change units found, chunking by change units")
            current_chunk = ""
            chars_per_chunk = int(self.max_token_limit / avg_token_per_char)
            logger.debug(f"Characters per chunk: {chars_per_chunk}")
            for unit in change_units:
                if len(current_chunk) + len(unit) > chars_per_chunk:
                    logger.debug(f"Adding chunk with {len(current_chunk)} characters")
                    chunks.append(current_chunk)
                    current_chunk = unit
                else:
                    if current_chunk:
                        current_chunk += "\n"
                    current_chunk += unit
            if current_chunk:
                logger.debug(f"Adding final chunk with {len(current_chunk)} characters")
                chunks.append(current_chunk)

        logger.info(f"Content split into {len(chunks)} chunks")
        return chunks

    def generate_summary_with_memory(self, contentdiff: str) -> SummaryResponse:
        logger.info("Starting summary generation with memory")
        logger.debug("Chunking content for memory-based processing")
        content_chunks = self.chunking_content(contentdiff)
        logger.info(f"Content split into {len(content_chunks)} chunks")
        collected_content = []
        collected_key_points = []
        collected_urls = []

        logger.debug("Initializing memory for chunk processing")
        memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=self.max_token_limit // 2,
            return_messages=True
        )

        logger.debug("Adding system message to memory")
        memory.chat_memory.add_message(SystemMessage(content="""
        You are a content analysis expert. Analyze content differences and extract key information.
        You will process multiple chunks, extracting key points and URLs for each.
        Finally, generate a JSON summary in the specified format.
        """))

        for i, chunk in enumerate(content_chunks):
            logger.info(f"Processing chunk {i+1}/{len(content_chunks)}")
            chunk_prompt = PromptTemplate(
                input_variables=["chunk_content"],
                template="""
                Analyze the following content difference chunk:

                {chunk_content}

                Provide in JSON format:
                1. content: List of content update summaries
                2. key_points: List of corresponding key points
                3. urls: List of URLs (2D array)

                Return only JSON, no extra text.
                """
            )

            logger.debug(f"Creating chain for chunk {i+1}")
            chunk_chain = chunk_prompt | self.llm
            try:
                logger.debug(f"Invoking LLM for chunk {i+1}")
                chunk_result = chunk_chain.invoke({"chunk_content": chunk})
                logger.debug(f"Received response for chunk {i+1}")
                chunk_content = chunk_result.content if hasattr(chunk_result, 'content') else str(chunk_result)
                logger.debug("Extracting JSON from chunk response")
                json_match = re.search(r'\{.*\}', chunk_content, re.DOTALL)
                if json_match:
                    logger.debug("JSON found in chunk response, parsing")
                    chunk_json = json.loads(json_match.group(0))
                    if 'content' in chunk_json and isinstance(chunk_json['content'], list):
                        logger.debug(f"Adding {len(chunk_json['content'])} content items")
                        collected_content.extend(chunk_json['content'])
                    if 'key_points' in chunk_json and isinstance(chunk_json['key_points'], list):
                        logger.debug(f"Adding {len(chunk_json['key_points'])} key points")
                        collected_key_points.extend(chunk_json['key_points'])
                    if 'urls' in chunk_json and isinstance(chunk_json['urls'], list):
                        logger.debug(f"Adding {len(chunk_json['urls'])} URL lists")
                        collected_urls.extend(chunk_json['urls'])
                    logger.debug("Saving context to memory")
                    memory.save_context(
                        {"input": f"Chunk {i+1}:\n{chunk[:200]}..."},
                        {"output": f"Analysis:\n{chunk_content[:200]}..."}
                    )
                else:
                    logger.warning(f"No JSON found in chunk {i+1} response")
            except Exception as e:
                logger.error(f"Chunk {i+1} processing failed: {e}")
                continue

        logger.info(f"Chunk processing complete. Collected {len(collected_content)} content items, {len(collected_key_points)} key points, and {len(collected_urls)} URL lists")
        logger.debug("Creating final prompt template")
        final_prompt_template = PromptTemplate(
            input_variables=["collected_content", "collected_key_points", "collected_urls", "format_instructions"],
            template="""
            Generate a final summary from the collected information:

            Content updates: {collected_content}
            Key points: {collected_key_points}
            URLs: {collected_urls}

            Return JSON in this format:

            {format_instructions}

            Notes:
            1. Ensure content and key_points correspond one-to-one.
            2. url_list is a 2D array for each key point's URLs.
            3. Calculate word_count (characters, no punctuation/spaces).
            4. Merge or remove duplicate content.
            5. Return only JSON.
            """
        )

        logger.debug("Creating final chain")
        final_chain = final_prompt_template | self.llm
        retries = 0
        last_exception = None
        raw_response = None

        while retries < self.max_retries:
            try:
                logger.debug(f"Attempt {retries+1}/{self.max_retries} to generate final summary")
                logger.debug("Invoking final chain")
                raw_response = final_chain.invoke({
                    "collected_content": collected_content,
                    "collected_key_points": collected_key_points,
                    "collected_urls": collected_urls,
                    "format_instructions": self.parser.get_format_instructions()
                })
                logger.debug("Final chain response received")
                raw_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
                logger.debug("Extracting JSON from final response")
                json_content = self.extract_json(raw_content)
                logger.debug("Parsing final response")
                response = self.parser.parse(json_content)
                logger.debug("Final response parsed successfully")

                if not response.generated_at:
                    logger.debug("Setting generated_at timestamp")
                    response.generated_at = datetime.now().isoformat()
                if response.word_count == 0 and response.content:
                    logger.debug("Calculating word count")
                    content_text = "".join(response.content)
                    word_count = len(re.sub(r'[\s\p{P}]', '', content_text, flags=re.UNICODE))
                    response.word_count = word_count
                    logger.debug(f"Word count calculated: {word_count}")
                if len(response.url_list) < len(response.key_points):
                    logger.debug("Adding empty URL lists for missing key points")
                    for _ in range(len(response.key_points) - len(response.url_list)):
                        response.url_list.append([])
                response.raw_response = raw_content
                logger.debug("Summary with memory generated successfully")
                logger.info(f"Summary with memory completed with status: {response.status}")
                return response

            except Exception as e:
                logger.error(f"Summary with memory failed: {e}")
                last_exception = e
                retries += 1
                if retries < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)

        logger.error(f"All retries failed: {str(last_exception)}")
        logger.info("Returning error response")
        return SummaryResponse(
            content=[],
            key_points=[],
            url_list=[],
            word_count=0,
            generated_at=datetime.now().isoformat(),
            status="error",
            error_message=f"Summary with memory failed: {str(last_exception)}",
            raw_response=str(raw_response) if raw_response else "No response"
        )

# Test the agent
if __name__ == "__main__":
    # Sample content differences
    sample_contentdiff = """
    "[\"\"Changed: '1' -> '2 分钟前\\n.\\nAIbase\\nFlower Labs 颠覆AI应用模式，2360万美元打造首个全开放混合计算平台\\n人工智能正在以前所未有的速度融入我们的日常应用，而一家名为Flower Labs的初创公司正以革命性的方式改变AI模型的部署和运行方式。这家获得Y Combinator支持的新锐企业近日推出了Flower Intelligence，一个创新的分布式云平台，专为在移动设备、个人电脑和网络应用中提供AI模型服务而设计。Flower Intelligence的核心优势在于其独特的混合计算策略。该平台允许应用程序在本地设备上运行AI模型，既保证了速度，又增强了隐私保护。当需要更强大的计算能力时，系统会在获得用户同意的情况下，无\\n7'\"\", \"\"Added: '美国埃隆大学的一项调查显示，5'\"\", \"\"Added: '%的美国成年人都曾使用过像ChatGPT、Gemini、Claude这样的AI大语言模型。这项由北卡罗来纳州埃隆大学\"想象数字未来中心\"在'\"\", \"\"Added: '月份开展的调查，选取了500名受访者。结果发现，在使用过AI的人群中，34%的人表示至少每天会使用一次大语言模型。其中，ChatGPT最受欢迎，72%的受访者都用过;谷歌的Gemini位居第二，使用率为50% 。图源备注：图片由AI生成，图片授权服务商Midjourney越来越多的人开始和AI聊天机器人建立起特殊的关系。调查显示，38%的用户认为大语言模\\n27'\"\", \"\"Changed: '3' -> '9'\"\", \"\"Changed: '49' -> '55'\"\", \"\"Changed: '1' -> '2'\"\", \"\"Deleted: '\\n2 小时前\\n.\\nAIbase\\n叫板Sora？潞晨科技开源视频大模型Open-Sora 2.0，降本提速\\n听说过壕无人性的 OpenAI Sora 吧?动辄几百万美元的训练成本，简直就是视频生成界的\"劳斯莱斯\"。现在，潞晨科技宣布开源视频生成模型 Open-Sora2.0!仅仅花费了区区20万美元（相当于224张 GPU 的投入），就成功训练出了一个拥有 110亿参数的商业级视频生成大模型。性能直追\"OpenAI Sora \"别看 Open-Sora2.0成本不高，实力可一点都不含糊。它可是敢于叫板行业标杆 HunyuanVideo 和拥有300亿参数的 Step-Video 的狠角色。在权威评测 VBench 和用户偏好测试中，Open-Sora2.0的表现都令人刮目相看，多项关键指'\"]"
    """

    # Initialize and test the agent
    logger.info("Initializing SubscriptionAgent for testing")
    agent = SubscriptionAgent(max_retries=3, retry_delay=2, max_token_limit=300)
    logger.info("Starting summary generation test")
    summary_result = agent.generate_summary(sample_contentdiff)
    logger.info("Summary generation test completed")

    # Display the result
    logger.info("Displaying summary result")
    print(json.dumps(summary_result.dict(), indent=2, ensure_ascii=False))