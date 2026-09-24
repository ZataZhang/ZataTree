---
title: 科技月报-2025
description: ""
date: 2025-11-26T15:22:18+08:00
image: images/index/index.png
categories:
    - Knowledge
tags:
    - 科技月报：机器人又抢饭碗啦
---




# 2025-12

## claude skills

[text](https://zhuanlan.zhihu.com/p/1966598753134842902)

[深刻理解Claude Skills-构建AI时代的组织和个体进化之路-加速从AI Agent到Agentic AI演进-zhihu](https://zhuanlan.zhihu.com/p/1964987120679645931)

## deepseek推出数学模型

[text](https://mp.weixin.qq.com/s/9bE7IfkthJBdSgfTEKw2Ng)


# 2025-11

## Google Gemini API File Search / Long Context 

[ RAG被判死刑：Google用一行API架空工程师！](https://mp.weixin.qq.com/s/6A4Dk14MejdvXdPSnBVfbA)

### 1. 核心架构思维转变

Google 的方案并不是传统的 RAG（检索），而是基于 **Long Context (长上下文)** 的全量处理。

| 特性 | 传统 RAG (LangChain + VectorDB) | Google Gemini File API |
| :--- | :--- | :--- |
| **处理逻辑** | 文档切片 -> 向量化 -> 相似度检索 -> 只有片段进 LLM | 全文档上传 -> Token化 -> **整个文档进 Context** -> LLM 原生注意力机制 |
| **优势** | 成本低，适合海量非结构化数据 (TB级) | **精度极高**，具备跨段落推理能力，支持复杂图表/表格理解 |
| **劣势** | 丢失上下文，图表/表格处理困难 | Token 消耗大 (需配合 Context Caching)，受限于 Context Window (目前 1M/2M) |

---

### 2. 环境准备

需要安装 Google 官方 Python SDK：

```bash
pip install -U google-generativeai
````

获取 API Key: [Google AI Studio](https://aistudio.google.com/)

-----

### 3. Python 实战代码 (MVP)

这是一个最小可行性脚本，包含了**文件上传**、**状态轮询**和**生成回答**的全流程。

```python
import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# ================= 配置区域 =================
# 建议将 API Key 放入环境变量: export GEMINI_API_KEY="your_key"
API_KEY = os.getenv("GEMINI_API_KEY")
FILE_PATH = "technical_spec.pdf"  # 替换为你的测试文件路径 (支持 PDF, CSV, TXT, MD 等)
MODEL_NAME = "gemini-1.5-flash-002" # 推荐: flash-002 (快/便宜) 或 pro-002 (强)
# ===========================================

genai.configure(api_key=API_KEY)

def upload_and_wait(path, mime_type=None):
    """
    上传文件并阻塞直到处理完成。
    Google 需要时间对大文件进行预处理（Token化/索引）。
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件未找到: {path}")

    print(f"🚀 正在上传: {path} ...")
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"✅ 上传成功. URI: {file.uri}")
    print(f"⏳ 等待文件处理 (状态: {file.state.name})...")

    # 轮询状态直到 ACTIVE
    while file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(2)
        file = genai.get_file(file.name)
    
    if file.state.name != "ACTIVE":
        raise Exception(f"❌ 文件处理失败: {file.state.name}")
    
    print("\n🎉 文件就绪!")
    return file

def main():
    try:
        # 1. 上传文件
        # 如果是纯文本，mime_type 可不填，PDF 建议显式指定 application/pdf
        your_file = upload_and_wait(FILE_PATH)

        # 2. 初始化模型
        # 关闭安全过滤以避免误杀技术文档内容
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            safety_settings=safety_settings,
            system_instruction="你是一个资深技术专家。请基于提供的文件内容回答问题。引用原文时请尽量精确。"
        )

        # 3. 发起提问 (Long Context 模式)
        # 提示：你可以在列表中传入多个 file 对象
        prompt = "请总结这份文档的核心架构，并提取出所有的数据库 Schema 定义（如果有）。"
        
        print(f"\n🤖 正在思考 ({MODEL_NAME})...")
        start_time = time.time()
        
        response = model.generate_content(
            [your_file, prompt],
            request_options={"timeout": 600} # 大文件处理可能较慢
        )
        
        print(f"⏱️ 耗时: {time.time() - start_time:.2f}s")
        print("-" * 30)
        print(response.text)
        print("-" * 30)

        # 4. (可选) 查看引用元数据
        if response.candidates[0].citation_metadata:
            print(f"📚 引用来源: {response.candidates[0].citation_metadata}")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    
    # 5. 清理资源 (根据需求决定是否保留文件)
    # print("正在删除云端文件...")
    # genai.delete_file(your_file.name)

if __name__ == "__main__":
    main()
```

-----

### 4\. 关键测试点 (PoC 验证清单)

在验证此方案是否能替代现有 RAG 时，请着重测试以下三点：

1.  **多模态理解能力 (Multimodal RAG)**

      * **测试素材：** 包含系统架构图、流程图或复杂数据表格的 PDF。
      * **Prompt：** "根据图 3 的架构图，解释数据是如何流转的？"
      * **预期：** 传统 RAG 通常做不到这一点（OCR 丢失结构），Gemini 应该能准确识别。

2.  **跨段落/全局信息整合**

      * **测试素材：** 长篇技术白皮书或小说。
      * **Prompt：** "总结文档中提到的所有关于‘安全性’的约束，并按优先级排序。"
      * **预期：** 传统 RAG 容易漏掉没检索到的切片，Gemini 拥有全量上下文，召回率应接近 100%。

3.  **延迟与成本 (Latency & Cost)**

      * **观察：** 首次请求的延迟（Cold Start）。
      * **注意：** 如果文件非常大且需要频繁提问，必须使用 **Context Caching**（见下文）。

-----

### 5\. 进阶：Context Caching (降本增效)

如果你的场景是“**一个大文档，被反复提问**”（例如：员工手册 bot、API 文档助手），直接每次上传或传入 Token 会非常贵。

请使用 Google 的 **Context Caching** 功能：

  * **原理：** 支付低廉的存储费，将处理好的 Context 缓存在 Google 端。
  * **效果：** 后续提问无需再次计算 Input Token，大幅降低延迟和推理成本。

*文档参考：[Google AI Studio - Context Caching](https://ai.google.dev/gemini-api/docs/caching)*



# 2025-07
### 202507月第三周


#### AI Agent开发新突破

- **ART框架发布！用Python一键训练AI Agent，邮件搜索到游戏操控全能搞定**

    人工智能技术的快速发展为智能Agent的训练带来了全新机遇。近日，一款名为ART（Agent Reinforcement Trainer）的开源强化学习框架正式发布，引发开发者社区的广泛关注。该框架通过集成GRPO技术，为Python开发者提供了便捷工具，可训练AI Agent执行多步骤任务，如邮件搜索和游戏操控等。

    **ART框架核心特性：**
    - **强化学习新利器**: 专注于通过强化学习（RL）提升AI Agent的性能，使其能够从经验中学习并优化任务执行
    - **多模型支持**: 支持Qwen2.5、Qwen3、Llama和Kimi等多种语言模型，特别推荐使用Qwen2.5-7B等小型模型
    - **长期运行能力**: 支持构建能够处理多轮交互、递归调用子Agent或压缩历史记录的长期运行Agent
    - **客户端与服务器分离**: 采用模块化架构，极大降低了使用门槛

    **简单集成，开发者友好：**
    - **一键安装**: 仅需运行 `pip install art` 即可完成安装
    - **无缝对接**: ART客户端与现有代码库无缝对接，通过简单的Python命令即可集成强化学习功能
    - **云端支持**: 支持在本地GPU或云端ephemeral GPU环境中运行
    - **强大集成**: 与W&B、Langfuse和OpenPipe等平台集成，提供强大的可观测性和调试功能

    **多场景应用价值：**
    - **邮件搜索与自动化**: 训练的Agent能够高效完成多步骤邮件检索任务，快速定位目标邮件
    - **游戏开发**: 可训练AI Agent在复杂游戏环境中自主学习，在Atari游戏或自定义场景中实现智能决策
    - **多Agent协作**: 支持递归调用子Agent和多轮交互，适合开发复杂的多Agent系统

    **技术优势：**
    - **GRPO算法**: 基于GRPO算法，通过并行执行多次rollout收集数据，结合最新检查点进行迭代训练
    - **模型兼容性**: 兼容大多数vLLM和HuggingFace Transformers支持的因果语言模型
    - **稳定性保证**: 确保模型在长期任务中的稳定性和高效性

    **项目地址**: https://github.com/OpenPipe/ART

    **未来展望**: ART开发团队表示，未来将扩展框架功能，支持多模态数据处理和超长上下文推理，满足更复杂的任务需求。其开源特性和模块化设计，使得中小型团队和个人开发者也能快速构建高性能Agent，打破了传统强化学习框架的技术壁垒。


#### AI视频生成再次突破

- **MirageLSD：首个直播流扩散AI模型震撼发布**

    近日，全球首个人工智能直播流扩散（Live-Stream Diffusion，LSD）模型MirageLSD正式发布，其强大的实时视频转换能力引发行业热议。这款由Decart AI团队打造的创新模型，能够以不到40毫秒的超低延迟，将任意视频流实时转换为用户期望的场景。

    **核心技术突破：**
    - **超低延迟**: 小于40毫秒的响应延迟，24帧/秒运行速度
    - **实时转换**: 支持摄像头、视频聊天、屏幕录制、游戏画面等任意视频流输入
    - **无限生成**: 突破传统模型长度限制，支持无限长度视频流处理
    - **效率提升**: 整体效率提升超过100倍，彻底打破时延和长度瓶颈

    **创新应用场景：**
    - **实时场景转换**: 将普通视频通话变成星际冒险，木棒对决变成光剑大战
    - **手势控制**: 通过简单手势实时改变背景、服装和场景
    - **快速游戏开发**: 30分钟内构建一款游戏，自动处理所有图形效果
    - **直播增强**: 主播可实时改变直播场景和视觉效果
    - **虚拟换装**: 为电商和时尚行业提供创新展示方式

    **技术优势：**
    - **Diffusion Forcing技术**: 基于逐帧去噪和历史增强训练
    - **抗漂移训练**: 解决传统自回归模型的误差累积问题
    - **CUDA Megakernel优化**: 显著提升GPU运行效率
    - **时间一致性**: 保持长时间生成中的画面质量和连贯性

    **体验地址**: https://mirage.decart.ai/

#### AI语音技术突破

- **AI语音，已超乎想象**
    
    如果你对AI语音的印象还停留在抖音里机械又没感情的复读机效果，那你就Out了。最新的AI语音技术已经达到了令人震撼的水平，生成一段高质量音频只需要几十秒、几毛钱。

    **ElevenLabs v3 核心能力：**
    - **自然流畅的语音合成**: 生成的语音自然、有感情、有气息，很难分辨出是合成的
    - **情绪控制**: 支持excited（兴奋）等情绪指令，语气词包含吸气、换气声音
    - **音调调整**: 支持Whisper等风格指令，可压低人声或调整说话风格
    - **音效生成**: 不仅能生成人声，还能生成咀嚼、狗叫、下雨等各种音效
    - **多语言混合**: 一句话里说多国语言，完全保留原本风格和音色
    - **多人对白**: 一次性生成多人对话，贴上台词即可生成小剧情
    - **声音设计**: 通过文本提示词创造全新的人声，无版权问题
    - **声音克隆**: 克隆任意人声，用该人声说出任何话

    **使用方法**: 访问 https://elevenlabs.io/app/speech-synthesis/text-to-speech ，每月有10000字免费额度。

#### AI视频生成重大突破

- **Lightricks 发布 LTXV 模型更新：图像到视频生成突破60秒**

    Lightricks 宣布其 AI 视频生成模型 LTX-Video（LTXV）迎来重大更新，新增支持生成长达 **60秒** 的图像到视频内容。这一突破性进展打破了行业常规的8秒限制，使 LTXV 成为首款支持实时流式生成长篇 AI 视频的开源模型。

    **核心技术突破：**
    - **60秒视频生成**: 通过自回归流式架构，从单一图像生成长达60秒的高质量视频
    - **实时流式传输**: 首秒内容几乎瞬时呈现，随后持续构建场景
    - **高分辨率输出**: 支持768x512或更高分辨率（如1216x704），帧率24FPS
    - **多尺度渲染**: 先以低分辨率捕捉粗略动作，再逐步优化细节

    **实时控制功能：**
    - **动态场景控制**: 视频生成过程中实时调整姿势、深度或风格等元素
    - **IC-LoRA 技术**: 持续应用控制信号，实现对视频细节的精准把控
    - **多种生成模式**: 支持文本到视频、图像到视频、关键帧动画以及视频扩展

    **高效性能：**
    - **130亿参数**模型架构，bfloat16精度优化
    - **硬件友好**: 消费级GPU（RTX4090/5090）即可运行，最低8GB VRAM需求
    - **超快速度**: H100GPU上4秒内生成5秒视频，RTX4080上生成768x512视频仅需45秒

    **开源优势**: 代码和权重已在GitHub和Hugging Face免费提供，配套LTX-Video-Trainer和ComfyUI集成工具。

#### 开发工具更新

- **SuperClaude** - 扩展 Claude Code 的 Python 框架，提供专门的命令、角色和 MCP 服务器集成。通过智能路由、任务自动化和多阶段编排来增强开发工作流程。

    - **核心框架**: 9个综合文档文件，指导 Claude Code 行为
    - **命令系统**: 16个专门的斜杠命令，用于常见开发任务
    - **角色系统**: 11个基于上下文自动激活的领域专家AI
    - **MCP集成**: 外部工具连接（Context7、Sequential、Magic、Playwright）
    - **安装系统**: 统一的CLI安装器，支持模块化组件选择

    [GitHub地址](https://github.com/NomenAK/SuperClaude)

- **Traycer** - VSCode的AI编程利器，处理大型代码库表现出色

    Traycer作为一款专为Visual Studio Code设计的AI编程助手工具，正迅速在开发者社区中崭露头角。这款由TraycerAI开发的VSCode插件以其强大的任务拆解、代码规划与实时分析能力，显著提升了开发者的编码效率。
    产品入口：https://traycer.ai

- **Augment Code Remote Agent** - 云端代码执行解决方案
    
    将代码push到GitHub后，通过云服务器远程执行agent，实现并行工作。授权后可访问私有仓库，本地电脑可以关机，代码在云端继续执行。



### 2025年07月第一周

#### 新闻

- 大而美法案
    增加美国赤字（拜登之前花了很多钱，导致特朗普现在举债额度很少）
    将会先降息，然后再扩表
    特朗普对于减税的问题，可能会导致以后更难收税
    ![大而美](../科技月报-2025-07/images/index/image.png)


#### 项目
|项目地址|描述|
|---|---|
|[github](https://github.com/Paper2Poster/Paper2Poster) | Paper2Poster: Multimodal Poster Automation from Scientific Papers从科学论文自动生成多模态海报的项目|
|[github](https://github.com/Yuliang-Liu/MonkeyOCR)|很牛的解析模型|







### 2025年06月第四周

#### 新闻

#### 项目

|||
|-----|-----|
| monkeyocr - 非常好的pdf解析工具，感觉效果会比pdf2zh那个好非常多|- [github-monkeyocr](https://github.com/Yuliang-Liu/Monkey)|
|现一款刚刚开源的Python打包工具：PyFuze|[wechat](https://mp.weixin.qq.com/s/BkIQdK3G803GWZep-ODKMA)|
|Claudia发布！优雅界面赋能Claude Code，跨平台AI编程新体验|[aibase](https://www.aibase.com/zh/news/19207)|
|面向初学者的机器学习教程|[github](https://github.com/microsoft/ML-For-Beginners)|
|可以把在线的对话封装成api|- [minimax-free-api](https://github.com/LLM-Red-Team/minimax-free-api)|


#### 其他
##### Gemini Cli已发布， 对标claude code
[Gemini Cli已发布， 对标claude code](https://www.youtube.com/watch?v=v41xKxZmygU)
评论说效果似乎不如claude code

##### 1panel v2版本 社区版两点

![1panel v2免费版升级](../科技月报-2025-07/images/index/image.png)


### 2025年06月第一周

#### 新闻



#### 项目

|---|
|-----|
|- OpenAudio 发布开源 TTS 模型 S1-Mini：0.5B 参数打造超自然 AI 语音|
|- 全球领先的 AI 语音技术公司 ElevenLabs 正式发布了其最新文本转语音模型 Eleven v3（Alpha 版），被誉为迄今最具表现力的 AI 语音模型。这一突破性进展不仅提升了语音合成的自然度和情感表达能力，还为内容创作者和开发者提供了更强大的工具，助力视频、音频书和多媒体工具的开发。|



#### 其他
#####  google vertex 是什么？

**Google Vertex AI** 是一个由 Google Cloud提供的统一机器学习平台，旨在帮助开发者和数据科学家更轻松、更快速地构建、部署和扩展机器学习 (ML) 模型。它将 Google Cloud 内部用于机器学习的所有工具整合到一个统一的界面和 API 中，从而简化了从数据准备到模型部署和管理的整个机器学习工作流程。

可以把它想象成一个一站式的机器学习“车间”，无论是初学者还是专家，都可以在这里找到合适的工具来完成他们的项目。

---

**核心理念与目标**

Vertex AI 的核心理念是**简化机器学习的开发流程**。在过去，一个机器学习项目通常需要在多个不同的服务和工具之间切换，例如一个用于数据处理，另一个用于模型训练，还有一个用于模型部署。这个过程非常繁琐且容易出错。

Vertex AI 的目标就是解决这个问题，它将整个机器学习生命周期（MLOps）的各个阶段整合在一起，包括：

* **数据准备**：连接到各种数据源，并使用工具进行数据清洗、标注和预处理。
* **模型构建与训练**：利用 AutoML（自动化机器学习）或编写自定义代码来训练模型。
* **模型评估与管理**：在统一的模型注册表中跟踪、评估和管理所有模型版本。
* **模型部署与预测**：将模型轻松部署到生产环境中，并提供在线预测或批量预测。
* **模型监控**：持续监控已部署模型的性能，并检测数据漂移或概念漂移。

---

**主要功能与工具**

Vertex AI 提供了涵盖整个机器学习工作流程的丰富工具集：

| 功能类别 | 主要工具和特点 |
| :--- | :--- |
| **统一环境** | **Vertex AI Workbench**: 基于 Jupyter 的完全托管、可扩展的企业级计算环境，预装了数据科学和机器学习所需的各种库。 |
| **数据准备** | **Vertex AI Feature Store**: 一个集中的特征存储库，用于在不同模型之间共享、重用和提供机器学习特征。 |
| | **数据标注**: 提供数据标注服务，可用于图像、视频、文本等多种数据类型。 |
| **模型训练** | **AutoML**: 无需编写代码即可训练高质量的自定义模型。只需提供数据，Vertex AI 就会自动探索不同的模型架构，为您找到最佳模型。支持图像、表格、文本和视频数据。 |
| | **自定义训练**: 为需要更精细控制的专家提供全面的支持。您可以使用 TensorFlow, PyTorch, Scikit-learn 或 XGBoost 等主流框架编写自己的训练代码，并在 Google 强大的基础设施上运行。 |
| **模型部署与服务** | **统一模型注册表**: 一个中央位置，用于管理、版本化和跟踪您的所有机器学习模型。 |
| | **端点 (Endpoint)**: 只需点击几下，即可将您的模型部署为可用于实时预测的端点。支持流量拆分，方便进行 A/B 测试。 |
| | **批量预测**: 对于不需要实时响应的大规模数据，可以进行批量预测。 |
| **MLOps (机器学习运维)** | **Vertex AI Pipelines**: 基于 Kubeflow Pipelines 构建，可帮助您编排和自动化您的机器学习工作流，实现工作流的可重复性和可扩展性。 |
| | **模型监控**: 自动监控已部署模型的性能和输入数据，以检测是否存在偏移（skew）或漂移（drift），并及时发出警报。 |
| **生成式 AI (Generative AI)** | **Vertex AI Gemini API**: 可以访问 Google 最先进的多模态基础模型 Gemini，用于构建各种生成式 AI 应用。 |
| | **Model Garden**: 提供对 Google 和开源基础模型（Foundation Models）的访问，开发者可以轻松地发现、测试和部署这些模型，并进行微调。 |

---

**主要优势**

* **加速模型开发与部署**: 传统的机器学习项目可能需要数月时间，而借助 Vertex AI 的 AutoML 和简化的工作流程，可以将时间缩短到几天。
* **降低技术门槛**: AutoML 功能让没有深厚机器学习背景的开发者也能构建强大的模型。
* **提高团队协作效率**: 统一的平台和共享的工具（如 Feature Store 和模型注册表）使得数据科学家、机器学习工程师和开发者之间的协作更加顺畅。
* **强大的可扩展性与性能**: 背靠 Google Cloud 强大的基础设施，无论是训练还是预测，都能够轻松应对大规模的需求。
* **全面的 MLOps 支持**: 提供了从数据到部署再到监控的端到端 MLOps 工具，帮助企业实现机器学习流程的自动化和标准化，确保模型的质量和可靠性。
* **拥抱前沿的生成式 AI**: 紧跟技术趋势，内置了对 Gemini 等先进生成式 AI 模型的支持，让开发者可以轻松构建下一代 AI 应用。

---

**适用场景**

Google Vertex AI 适用于各种规模和行业的机器学习应用，例如：

* **零售业**: 用于构建产品推荐系统、需求预测和客户流失分析模型。
* **金融业**: 用于欺诈检测、信用风险评估和算法交易。
* **医疗保健**: 用于医学影像分析、疾病预测和个性化治疗方案的制定。
* **媒体与娱乐**: 用于内容推荐、观众行为分析和自动内容审核。
* **制造业**: 用于预测性维护、质量控制和供应链优化。

总而言之，**Google Vertex AI 是一个功能强大且全面的机器学习平台，它通过统一的工具和简化的流程，极大地降低了构建和部署高质量机器学习模型的复杂性，是企业和开发者在当今 AI 时代进行创新的重要利器。**
**Google Vertex AI：一站式机器学习与人工智能开发平台**

Google Vertex AI 是一个由 Google Cloud 提供的统一机器学习（ML）平台，旨在帮助开发者和数据科学家更轻松、更快速地构建、部署和扩展机器学习模型与人工智能（AI）应用。它整合了从数据准备、模型训练、模型评估到最终部署和管理的整个机器学习工作流程，提供了一套完整的工具集，无论是初学者还是专家都能高效地利用其进行 AI 开发。

---

**核心理念：统一与简化**

在 Vertex AI 推出之前，机器学习的各个阶段——例如使用 AutoML 进行自动化模型训练和使用自定义代码进行模型开发——通常需要通过不同的服务和界面来完成。Vertex AI 的核心优势在于**将整个机器学习流程统一到一个平台和 API**下。这意味着团队可以在同一个环境中进行数据工程、数据科学和机器学习工程的协作，从而大大提高了开发效率和协作的流畅性。

---

**主要功能与核心组件**

Vertex AI 提供了涵盖机器学习全生命周期的丰富功能，主要包括以下几个核心组件：

* **Vertex AI Studio**：这是一个用于快速测试、调整和部署生成式 AI 模型的可视化界面。开发者可以在这里与 Google 最先进的模型（如 Gemini）进行交互，通过编写提示（Prompt）来生成文本、图片、代码等内容，并根据特定需求对模型进行定制。

* **Model Garden（模型花园）**：Model Garden 提供了一个丰富的模型库，其中包含了 Google 自主研发的先进模型（如 Gemini、Imagen 等）、第三方模型以及众多流行的开源模型。用户可以在这里发现、测试、自定义和部署最适合其业务场景的模型。

* **AutoML**：对于没有深厚机器学习背景的用户，AutoML 提供了强大的自动化能力。用户只需提供结构化数据、图像、文本或视频，AutoML 就能自动训练出高性能的模型，无需编写任何代码。

* **Custom Training（自定义训练）**：对于需要更高灵活性的专家用户，Vertex AI 提供了完全受控的自定义训练环境。开发者可以使用自己喜欢的机器学习框架（如 TensorFlow, PyTorch, scikit-learn），编写自定义训练代码，并进行超参数调整。

* **Vertex AI Workbench**：这是一个基于 Jupyter 的集成开发环境，为数据科学家提供了从数据探索、分析到模型训练和部署的统一笔记本体验。它深度集成了 Google Cloud 的其他数据服务，如 BigQuery 和 Cloud Storage，方便用户无缝访问和处理数据。

* **MLOps 工具链**：Vertex AI 提供了一整套 MLOps（机器学习运维）工具，包括 **Vertex AI Pipelines** 用于构建和自动化工作流，**Vertex AI Feature Store** 用于管理和共享特征，以及 **Model Registry** 和 **Monitoring** 服务，帮助用户管理、版本控制和监控已部署模型的性能，确保其长期稳定运行。

---

**核心优势**

选择 Google Vertex AI 进行 AI 开发具有以下显著优势：

* **加速模型开发与部署**：通过统一的平台和强大的自动化工具，将模型从实验到生产部署的时间从数月缩短到数周甚至数天。
* **降低技术门槛**：AutoML 和 Vertex AI Studio 等工具使得没有专业机器学习知识的开发者也能构建和使用强大的 AI 模型。
* **强大的生成式 AI 能力**：可以直接访问和利用 Google 最前沿的生成式 AI 模型（如 Gemini），快速构建具备内容创作、对话、摘要等能力的下一代 AI 应用。
* **开放与灵活**：不仅支持 Google 的专有技术，还广泛兼容各类开源框架和第三方模型，为开发者提供了极大的灵活性和选择空间。
* **企业级的安全与可靠性**：依托于 Google Cloud 强大的基础设施，Vertex AI 提供了企业级的安全性、数据治理和可扩展性，确保应用稳定可靠。

---

**典型应用场景**

Google Vertex AI 已经被广泛应用于各个行业，解决复杂的业务问题，典型的应用场景包括：

* **智能客服与聊天机器人**：利用生成式 AI 模型构建能理解并进行多轮对话的智能客服，提升用户体验。
* **个性化推荐**：训练推荐模型，为用户提供更精准的商品、内容或服务推荐。
* **图像与视频分析**：通过图像识别和视频内容分析，实现产品质检、内容审核、场景理解等功能。
* **欺诈检测**：分析交易数据，实时识别并预防金融欺诈行为。
* **文档处理与分析**：自动从大量文档中提取关键信息、进行摘要和分类。

总之，Google Vertex AI 是一个功能强大且全面的平台，它通过简化和加速机器学习的整个生命周期，让企业和开发者能够更专注于创新和解决实际问题，从而在人工智能时代获得竞争优势。



### 2025年05月第二周

#### 新闻

- Flow-GRPO技术大幅提升图像生成模型能力，解决复杂场景生成难题。
- manus开放注册，目前看免费版本明显不如gemini


#### 项目

- [18中RAG技术对比](https://apframework.com/blog/essay/2025-04-09-18-RAG-Techniques)
- [Google Agent白皮书解析：模型、工具与编排层全面指南](https://apframework.com/blog/essay/2025-02-16-Google-Agent)
- [Claude MCP 使用及搭建](https://apframework.com/blog/essay/2024-12-15-Claude-MCP)
- [聊天记录生成数字分身](https://github.com/xming521/WeClone)



#### 感悟



### 2025年05月第一周
#### 科技新闻

- Qwen3发布

#### github项目

- [全新的跨平台浏览器内核，浏览器界面使用Qt开发](https://github.com/LadybirdBrowser/ladybird)

- [分享github项目的github项目](https://github.com/521xueweihan/HelloGitHub)

- [aws推出的agent框架](https://github.com/awslabs/agent-squad?tab=readme-ov-file)


            主要功能
            智能意图分类：自动识别用户查询，并动态分配合适的 AI 代理进行处理。

            双语支持：框架支持 Python 和 TypeScript 两种语言。

            灵活的代理响应：支持 流式（streaming） 和 非流式 的响应方式。

            上下文管理：多个 AI 代理之间共享和维护对话上下文，确保连贯性。

            可扩展架构：用户可以轻松集成新的 AI 代理，或定制现有代理的能力。

            跨平台部署：支持 AWS Lambda、本地环境、云平台 等多种运行方式。

            内置 AI 代理与分类器：提供预构建的代理，支持各种应用场景。


- [实时的deepfake](https://github.com/hacksider/Deep-Live-Cam)

- [一个子托管的dashboard，感觉可以和我的Upick结合一下](https://github.com/glanceapp/glance?tab=readme-ov-file)

- [具有本机AI功能的公平代码工作流程自动化平台。将视觉构建与自定义代码，自宿主或云相结合，400+集成。](https://github.com/n8n-io/n8n)

- [电子书阅读器，支持多格式，pdf、EPUB等](https://github.com/koreader/koreader?tab=readme-ov-file)


- [huggingface推出的agent课程](https://github.com/huggingface/agents-course)

- [科技爱好者周刊](https://github.com/ruanyf/weekly/tree/master)







### 2025年04月第三周

#### 科技新闻

-  真我推出首款 AI 翻译耳机 Bud Air7 Pro，支持 32 种语言翻译！  [感觉如果再结合手机作为声音输出源，真香！]
- ​哥伦比亚大学退学生开发 “AI面试作弊神器”Interview Coder ，成功融资500万美元 [可能以后的面试形式会变一变，不在是像现在这样的八股文了]


#### github项目


- https://github.com/microsoft/markitdown 【微软推出，用于将各类文件转换为markdown，现在提供mcp】 期待度：★★★★★

- https://github.com/Byaidu/PDFMathTranslate 【多语言的pdf翻译转换工具】 期待度：★★★★★   ---- 20250423试了，效果还可以，而且我还是用的默认的google翻译，可能用ai会更好

![原始pdf](../科技周报：2025年04月第3周/images/index/image.png)
![翻译后的pdf](../科技周报：2025年04月第3周/images/index/image2.png)

- https://github.com/dgtlmoon/changedetection.io?tab=readme-ov-file 【监控网页变化】

- https://github.com/pocketbase/pocketbase?tab=readme-ov-file 【一个小型的后端数据库】

- https://github.com/drawdb-io/drawdb 【可视化的操作/创建数据库】

- https://github.com/microsoft/generative-ai-for-beginners 【面向初学者的生成式AI课程】
 


### 2025年03月第三周

#### 科技新闻

1. OpenAI Chat Playground升级为Prompts Playground 更好测试、迭代提示词
2. 百度正式发布文心大模型4.5及文心大模型X1，效果如何？
	https://www.zhihu.com/question/13661056614
3. 小米大模型团队登顶音频推理 MMAU 榜，受到DeepSeek-R1启发
4. 首个国产Agent开发框架!仓颉社区发布Cangjie Magic，原生支持鸿蒙等全平台!
5. 2025.3.18-Mistral开源Mistral-Small-3.1-24B   多模态、多语言，各项评分超过Gemma 3 27B、GPT-4o mini，OCR能力强。
6. 腾讯更新混元3D模型 新发布3D 2.0 MV（多视角效果更好）和3D 2.0 Mini（参数更小）。

#### github项目趋势
1. https://github.com/glanceapp/glance/tree/main?tab=readme-ov-file   像newsnow    
2. https://github.com/xpipe-io/xpipe  shell connection hub

3. https://github.com/calcom/cal.com    有点像滴答清单

4. https://github.com/langchain-ai/ollama-deep-researcher

5. https://github.com/patchy631/ai-engineering-hub  ai的教程

6. https://github.com/langchain-ai/ollama-deep-researcher   ollama

7. https://github.com/graviraja/MLOps-Basics 分周了解机器学习运维基础

8. https://github.com/block/goose?tab=readme-ov-file  agent-tool

