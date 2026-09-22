/**
 * 只读文件与改动查看器的前端交互。
 *
 * 数据全部来自本机只读接口（/api/info、/api/tree、/api/file、/api/changes、/api/diff），
 * 页面不做任何写入，也不做心跳轮询——一旦开始轮询，服务端的空闲自动回收就会静默
 * 失效（见 docs/guides/file-viewer.md 的回收策略一节）。
 */
(() => {
  "use strict";

  const FILES_VIEW = "files";
  const DIFF_VIEW = "diff";

  const elements = {
    repoName: document.getElementById("repo-name"),
    branchChip: document.getElementById("branch-chip"),
    tabFiles: document.getElementById("tab-files"),
    tabDiff: document.getElementById("tab-diff"),
    diffCount: document.getElementById("diff-count"),
    baselineSelect: document.getElementById("baseline-select"),
    filterInput: document.getElementById("filter-input"),
    treeTitle: document.getElementById("tree-title"),
    treeNote: document.getElementById("tree-note"),
    treeBody: document.getElementById("tree-body"),
    viewerPath: document.getElementById("viewer-path"),
    viewerMeta: document.getElementById("viewer-meta"),
    viewerBody: document.getElementById("viewer-body"),
    statusDot: document.getElementById("status-dot"),
    statusText: document.getElementById("status-text"),
    statusHint: document.getElementById("status-hint"),
  };

  /** 页面的全部可变状态；渲染只读它，用户操作只改它。默认落在改动视图。 */
  const viewState = {
    view: DIFF_VIEW,
    baseline: "worktree",
    selectedPath: "",
    collapsedDirectories: new Set(),
    filterText: "",
    filePaths: [],
    changedFiles: [],
    isDisconnected: false,
  };

  /**
   * 请求一个只读接口。
   * @param {string} requestUrl 接口地址。
   * @returns {Promise<{status: number, body: object}>} 应答状态码与 JSON 正文。
   */
  async function requestJson(requestUrl) {
    const response = await fetch(requestUrl, { headers: { Accept: "application/json" } });
    const responseBody = await response.json();
    return { status: response.status, body: responseBody };
  }

  /**
   * 切换到「服务已退出」状态：左树置灰不可点，内容区给出重新连接指引。
   * @param {string} failureMessage 失败说明，用于状态条。
   */
  function enterDisconnectedState(failureMessage) {
    viewState.isDisconnected = true;
    elements.treeBody.classList.add("is-stale");
    elements.statusDot.classList.add("down");
    elements.statusText.textContent = "服务已退出 · 运行 just view 重新连接";
    elements.baselineSelect.disabled = true;
    renderDisconnectedNotice(failureMessage);
  }

  /**
   * 在内容区渲染服务退出提示。
   * @param {string} failureMessage 失败说明。
   */
  function renderDisconnectedNotice(failureMessage) {
    elements.viewerPath.textContent = "服务已退出";
    elements.viewerMeta.textContent = "";
    elements.viewerBody.replaceChildren(
      buildNotice({
        isFailure: true,
        title: "服务已退出",
        paragraphs: [
          "查看器空闲到时限后会自动退出（默认 30 分钟无任何请求），也可以用 just view --stop 立刻回收。",
          "在仓库里重新执行 just view 会新起一个实例并打开新标签页，本页不再自动恢复。",
        ],
        hint: failureMessage ? `本次请求失败原因：${failureMessage}` : "",
      })
    );
  }

  /**
   * 转义要拼进 innerHTML 的文本。
   *
   * 提示块的段落走 innerHTML，而界面上的路径来自 git、文件名本身可以含 `& < >`
   * （例如 `a<b.md`），不转义会让提示块结构错乱。
   * @param {string} rawText 原始文本。
   * @returns {string} 转义后的文本。
   */
  function escapeHtmlText(rawText) {
    return rawText
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }

  /**
   * 构造一个内容区提示块。
   * @param {{isFailure?: boolean, title: string, paragraphs: string[], hint?: string}} noticeInput 提示内容。
   * @returns {HTMLElement} 提示块节点。
   */
  function buildNotice(noticeInput) {
    const noticeNode = document.createElement("div");
    noticeNode.className = noticeInput.isFailure ? "notice down" : "notice";
    const titleNode = document.createElement("h3");
    titleNode.textContent = noticeInput.title;
    noticeNode.append(titleNode);
    for (const paragraphText of noticeInput.paragraphs) {
      const paragraphNode = document.createElement("p");
      paragraphNode.innerHTML = paragraphText;
      noticeNode.append(paragraphNode);
    }
    if (noticeInput.hint) {
      const hintNode = document.createElement("p");
      hintNode.textContent = noticeInput.hint;
      noticeNode.append(hintNode);
    }
    return noticeNode;
  }

  /**
   * 执行一次接口调用并把网络失败统一转成「服务已退出」。
   * @param {() => Promise<unknown>} action 需要保护的调用。
   * @returns {Promise<boolean>} 调用是否成功完成。
   */
  async function guardAgainstServiceExit(action) {
    if (viewState.isDisconnected) {
      return false;
    }
    try {
      await action();
      return true;
    } catch (networkError) {
      enterDisconnectedState(networkError instanceof Error ? networkError.message : "");
      return false;
    }
  }

  /**
   * 读取 URL 上的初始视图、基线与直达路径。
   */
  function applyInitialQueryParameters() {
    const searchParameters = new URLSearchParams(window.location.search);
    const requestedView = searchParameters.get("view");
    if (requestedView === DIFF_VIEW || requestedView === FILES_VIEW) {
      viewState.view = requestedView;
    }
    const requestedBaseline = searchParameters.get("base");
    if (requestedBaseline) {
      viewState.baseline = requestedBaseline;
    }
    viewState.selectedPath = searchParameters.get("path") || "";
  }

  /**
   * 初始化页面：拉取仓库信息与文件树，然后按初始状态渲染。
   */
  async function initializeViewer() {
    applyInitialQueryParameters();
    const didLoad = await guardAgainstServiceExit(async () => {
      const infoResponse = await requestJson("/api/info");
      elements.repoName.textContent = infoResponse.body.repo_name;
      elements.branchChip.textContent = infoResponse.body.branch;
      window.document.title = `${infoResponse.body.repo_name} · 只读查看器`;
      renderBaselineOptions(infoResponse.body.baselines);

      const treeResponse = await requestJson("/api/tree");
      viewState.filePaths = treeResponse.body.paths;
    });
    if (!didLoad) {
      return;
    }

    expandToSelectedPath();
    if (viewState.view === DIFF_VIEW) {
      await loadChangedFiles();
    } else {
      renderTree();
      if (viewState.selectedPath) {
        await selectPath(viewState.selectedPath);
      } else {
        renderPlaceholder();
      }
    }
    renderViewTabs();
  }

  /**
   * 把后端给出的基线列表填进选择器。
   * @param {Array<{value: string, label: string}>} baselineOptions 可选的比较基线。
   */
  function renderBaselineOptions(baselineOptions) {
    elements.baselineSelect.replaceChildren();
    for (const baselineOption of baselineOptions) {
      const optionNode = document.createElement("option");
      optionNode.value = baselineOption.value;
      optionNode.textContent = baselineOption.label;
      elements.baselineSelect.append(optionNode);
    }
    const hasRequestedBaseline = baselineOptions.some(
      (baselineOption) => baselineOption.value === viewState.baseline
    );
    viewState.baseline = hasRequestedBaseline ? viewState.baseline : "worktree";
    elements.baselineSelect.value = viewState.baseline;
    elements.baselineSelect.disabled = viewState.view !== DIFF_VIEW;
  }

  /**
   * 展开直达路径上的全部祖先目录。
   */
  function expandToSelectedPath() {
    if (!viewState.selectedPath) {
      return;
    }
    const pathSegments = viewState.selectedPath.split("/");
    for (let segmentIndex = 0; segmentIndex < pathSegments.length; segmentIndex += 1) {
      viewState.collapsedDirectories.delete(pathSegments.slice(0, segmentIndex + 1).join("/"));
    }
  }

  /**
   * 读取当前基线下的改动文件列表。
   */
  async function loadChangedFiles() {
    const didLoad = await guardAgainstServiceExit(async () => {
      const changesResponse = await requestJson(
        `/api/changes?base=${encodeURIComponent(viewState.baseline)}`
      );
      if (changesResponse.status !== 200) {
        viewState.changedFiles = [];
        renderNotice(buildNotice({ title: "无法列出改动", paragraphs: [changesResponse.body.error] }));
        return;
      }
      viewState.changedFiles = changesResponse.body.files;
      elements.diffCount.textContent = String(changesResponse.body.totals.files);
      elements.diffCount.hidden = false;
      elements.statusHint.textContent =
        `基线 ${changesResponse.body.base_label} · ${changesResponse.body.totals.files} 个文件 ` +
        `+${changesResponse.body.totals.add} -${changesResponse.body.totals.del}`;
    });
    if (!didLoad) {
      return;
    }
    renderTree();
    const isSelectionStillVisible = viewState.changedFiles.some(
      (changedFile) => changedFile.path === viewState.selectedPath
    );
    if (isSelectionStillVisible) {
      await selectPath(viewState.selectedPath);
    } else {
      renderPlaceholder();
    }
  }

  /**
   * 渲染视图切换按钮与基线选择器的启用状态。
   */
  function renderViewTabs() {
    const isDiffView = viewState.view === DIFF_VIEW;
    elements.tabFiles.setAttribute("aria-selected", String(!isDiffView));
    elements.tabDiff.setAttribute("aria-selected", String(isDiffView));
    elements.baselineSelect.disabled = !isDiffView || viewState.isDisconnected;
    const treeTitleNode = document.createElement("b");
    treeTitleNode.textContent = isDiffView ? "改动文件" : "文件树";
    elements.treeTitle.replaceChildren(treeTitleNode);
  }

  /**
   * 在内容区渲染一个提示块。
   * @param {HTMLElement} noticeNode 提示块节点。
   */
  function renderNotice(noticeNode) {
    elements.viewerPath.textContent = "—";
    elements.viewerMeta.textContent = "";
    elements.viewerBody.replaceChildren(noticeNode);
  }

  /**
   * 渲染未选中文件时的空态。
   */
  function renderPlaceholder() {
    if (viewState.view === DIFF_VIEW) {
      renderNotice(
        buildNotice({
          title: viewState.changedFiles.length ? "选择一个改动文件" : "该基线下没有改动",
          paragraphs: [
            viewState.changedFiles.length
              ? "左侧列出的是该基线下有改动的文件，点开任意一个查看逐行改动。"
              : `当前基线（${elements.baselineSelect.value === "worktree" ? "工作区改动" : viewState.baseline}）与 HEAD 没有差异。`,
          ],
          hint: "提示：未加入版本控制且未被暂存的新文件不会出现在这里，与终端 git diff 的口径一致。",
        })
      );
      return;
    }
    renderNotice(
      buildNotice({
        title: "选择一个文件",
        paragraphs: ["左侧是本仓库的文件树，点开任意文件即可在右侧查看带行号与语法高亮的正文。"],
        hint: "快捷键：f 切文件视图、d 切改动视图、/ 聚焦过滤框。",
      })
    );
  }

  /**
   * 渲染左侧树；两个视图共用同一套目录树，只有叶子行与空态文案不同。
   *
   * 改动视图按目录分组，而不是铺成一长条扁平行：改动文件动辄成百上千，扁平列表既看不出
   * 改动集中在哪几个目录，长路径也会把真正要认的文件名挤出左栏。
   */
  function renderTree() {
    const isDiffView = viewState.view === DIFF_VIEW;
    const treeEntries = isDiffView
      ? viewState.changedFiles
      : viewState.filePaths.map((filePath) => ({ path: filePath }));
    const directoryTree = buildDirectoryTree(treeEntries);
    // 计数跟着当前这棵树走：改动视图下挂着仓库总文件数会与「改动文件」这个标题对不上。
    elements.treeNote.textContent = `${treeEntries.length} 个文件`;
    const filterText = viewState.filterText.trim().toLowerCase();
    const treeFragment = document.createDocumentFragment();
    appendDirectoryChildren(treeFragment, directoryTree, 0, filterText);
    if (!treeFragment.childNodes.length) {
      elements.treeBody.replaceChildren(buildTreeEmpty(emptyTreeMessage(isDiffView)));
      return;
    }
    elements.treeBody.replaceChildren(treeFragment);
  }

  /**
   * 左树的空态文案。
   * @param {boolean} isDiffView 是否处于改动视图。
   * @returns {string} 空态说明。
   */
  function emptyTreeMessage(isDiffView) {
    if (!isDiffView) {
      return "没有匹配过滤条件的文件。";
    }
    return viewState.changedFiles.length
      ? "没有匹配过滤条件的改动文件。"
      : "该基线下没有改动文件。";
  }

  /**
   * 构造一个改动文件叶子行：状态徽标 + 文件名 + 增删统计。
   * 目录上下文由所在层级表达，行内不再重复完整路径。
   * @param {{path: string, status: string, add: number|null, del: number|null}} changedFile 改动文件。
   * @param {number} depth 缩进层级。
   * @returns {HTMLElement} 条目节点。
   */
  function buildChangedFileRow(changedFile, depth) {
    const rowButton = document.createElement("button");
    rowButton.type = "button";
    rowButton.className = "node";
    rowButton.style.paddingLeft = `${8 + depth * 14}px`;
    rowButton.title = changedFile.path;
    rowButton.setAttribute("aria-selected", String(changedFile.path === viewState.selectedPath));
    rowButton.append(buildCaretPlaceholder());

    const badgeNode = document.createElement("span");
    badgeNode.className = `badge ${changedFile.status}`;
    badgeNode.textContent = changedFile.status;
    rowButton.append(badgeNode);

    const nameNode = document.createElement("span");
    nameNode.className = "name";
    const lastSlashIndex = changedFile.path.lastIndexOf("/");
    nameNode.textContent =
      lastSlashIndex >= 0 ? changedFile.path.slice(lastSlashIndex + 1) : changedFile.path;
    rowButton.append(nameNode);

    const statNode = document.createElement("span");
    statNode.className = "stat";
    if (changedFile.add === null || changedFile.del === null) {
      const binaryNode = document.createElement("span");
      binaryNode.className = "badge";
      binaryNode.textContent = "二进制";
      statNode.append(binaryNode);
    } else {
      statNode.append(buildStatNode("add", `+${changedFile.add}`));
      statNode.append(buildStatNode("del", `-${changedFile.del}`));
    }
    rowButton.append(statNode);

    rowButton.addEventListener("click", () => {
      void selectPath(changedFile.path);
    });
    return rowButton;
  }

  /**
   * 构造一个增删统计节点。
   * @param {"add"|"del"} statKind 统计类型。
   * @param {string} statText 统计文本。
   * @returns {HTMLElement} 统计节点。
   */
  function buildStatNode(statKind, statText) {
    const statNode = document.createElement("span");
    statNode.className = statKind;
    statNode.textContent = statText;
    return statNode;
  }

  /**
   * 构造占位用的折叠箭头，让改动视图的条目与文件树条目左缘对齐。
   * @returns {HTMLElement} 占位节点。
   */
  function buildCaretPlaceholder() {
    const caretNode = document.createElement("span");
    caretNode.className = "caret";
    return caretNode;
  }

  /**
   * 构造文件树的空态节点。
   * @param {string} emptyMessage 空态说明。
   * @returns {HTMLElement} 空态节点。
   */
  function buildTreeEmpty(emptyMessage) {
    const emptyNode = document.createElement("div");
    emptyNode.className = "tree-empty";
    emptyNode.textContent = emptyMessage;
    return emptyNode;
  }

  /**
   * 把扁平的条目列表组装成目录树。
   *
   * 文件视图传 `{path}`，改动视图传改动文件对象；叶子节点把原条目留在 `payload` 里，
   * 于是两种叶子行都能从同一棵树渲染。
   * @param {Array<{path: string}>} treeEntries 每条含仓库相对路径。
   * @returns {{name: string, path: string, isDirectory: boolean, children: Map, payload: object|null}} 根节点。
   */
  function buildDirectoryTree(treeEntries) {
    const rootNode = {
      name: "",
      path: "",
      isDirectory: true,
      children: new Map(),
      payload: null,
    };
    for (const treeEntry of treeEntries) {
      const pathSegments = treeEntry.path.split("/");
      let currentNode = rootNode;
      for (let segmentIndex = 0; segmentIndex < pathSegments.length; segmentIndex += 1) {
        const pathSegment = pathSegments[segmentIndex];
        if (!currentNode.children.has(pathSegment)) {
          currentNode.children.set(pathSegment, {
            name: pathSegment,
            path: pathSegments.slice(0, segmentIndex + 1).join("/"),
            isDirectory: segmentIndex < pathSegments.length - 1,
            children: new Map(),
            payload: null,
          });
        }
        currentNode = currentNode.children.get(pathSegment);
      }
      currentNode.payload = treeEntry;
    }
    return rootNode;
  }

  /**
   * 递归追加目录下的可见节点。
   * @param {DocumentFragment} treeFragment 目标片段。
   * @param {{name: string, path: string, isDirectory: boolean, children: Map}} directoryNode 当前目录。
   * @param {number} depth 缩进层级。
   * @param {string} filterText 小写过滤词；非空时只保留命中路径及其祖先。
   */
  function appendDirectoryChildren(treeFragment, directoryNode, depth, filterText) {
    const sortedChildren = [...directoryNode.children.values()].sort(compareTreeNode);
    for (const childNode of sortedChildren) {
      if (!matchesFilter(childNode, filterText)) {
        continue;
      }
      if (childNode.isDirectory) {
        treeFragment.append(buildDirectoryRow(childNode, depth, filterText));
        if (!viewState.collapsedDirectories.has(childNode.path)) {
          appendDirectoryChildren(treeFragment, childNode, depth + 1, filterText);
        }
      } else if (viewState.view === DIFF_VIEW) {
        treeFragment.append(buildChangedFileRow(childNode.payload, depth));
      } else {
        treeFragment.append(buildFileRow(childNode, depth));
      }
    }
  }

  /**
   * 判断节点是否命中过滤条件；目录在本目录自身或任一后代命中时保留。
   * @param {{name: string, path: string, isDirectory: boolean, children: Map}} treeNode 待判定节点。
   * @param {string} filterText 小写过滤词。
   * @returns {boolean} 是否应当显示。
   */
  function matchesFilter(treeNode, filterText) {
    if (!filterText) {
      return true;
    }
    if (treeNode.path.toLowerCase().includes(filterText)) {
      return true;
    }
    if (!treeNode.isDirectory) {
      return false;
    }
    return [...treeNode.children.values()].some((childNode) =>
      matchesFilter(childNode, filterText)
    );
  }

  /**
   * 排序：目录在前，同类按名称排序。
   * @param {{name: string, isDirectory: boolean}} leftNode 左节点。
   * @param {{name: string, isDirectory: boolean}} rightNode 右节点。
   * @returns {number} 排序比较值。
   */
  function compareTreeNode(leftNode, rightNode) {
    if (leftNode.isDirectory !== rightNode.isDirectory) {
      return leftNode.isDirectory ? -1 : 1;
    }
    return leftNode.name.localeCompare(rightNode.name);
  }

  /**
   * 构造目录行。
   * @param {{name: string, path: string, children: Map}} directoryNode 目录节点。
   * @param {number} depth 缩进层级。
   * @param {string} filterText 小写过滤词；命中目录强制展开，便于看到命中项。
   * @returns {HTMLElement} 目录行。
   */
  function buildDirectoryRow(directoryNode, depth, filterText) {
    const isCollapsed =
      !filterText && viewState.collapsedDirectories.has(directoryNode.path);
    const rowButton = document.createElement("button");
    rowButton.type = "button";
    rowButton.className = "node";
    rowButton.style.paddingLeft = `${8 + depth * 14}px`;
    rowButton.setAttribute("aria-expanded", String(!isCollapsed));

    const caretNode = document.createElement("span");
    caretNode.className = "caret";
    caretNode.textContent = isCollapsed ? "▸" : "▾";
    rowButton.append(caretNode);

    const nameNode = document.createElement("span");
    nameNode.className = "name";
    nameNode.textContent = `${directoryNode.name}/`;
    rowButton.append(nameNode);

    if (!filterText) {
      const countNode = document.createElement("span");
      countNode.className = "chip";
      countNode.textContent = String(countFileLeaves(directoryNode));
      rowButton.append(countNode);
    }

    rowButton.addEventListener("click", () => {
      if (viewState.collapsedDirectories.has(directoryNode.path)) {
        viewState.collapsedDirectories.delete(directoryNode.path);
      } else {
        viewState.collapsedDirectories.add(directoryNode.path);
      }
      renderTree();
    });
    return rowButton;
  }

  /**
   * 统计目录下的文件数。
   * @param {{isDirectory: boolean, children: Map}} treeNode 目录节点。
   * @returns {number} 文件数。
   */
  function countFileLeaves(treeNode) {
    if (!treeNode.isDirectory) {
      return 1;
    }
    let fileCount = 0;
    for (const childNode of treeNode.children.values()) {
      fileCount += countFileLeaves(childNode);
    }
    return fileCount;
  }

  /**
   * 构造文件行。
   * @param {{name: string, path: string}} fileNode 文件节点。
   * @param {number} depth 缩进层级。
   * @returns {HTMLElement} 文件行。
   */
  function buildFileRow(fileNode, depth) {
    const rowButton = document.createElement("button");
    rowButton.type = "button";
    rowButton.className = "node";
    rowButton.style.paddingLeft = `${8 + depth * 14}px`;
    rowButton.setAttribute("aria-selected", String(fileNode.path === viewState.selectedPath));
    rowButton.append(buildCaretPlaceholder());

    const nameNode = document.createElement("span");
    nameNode.className = "name";
    nameNode.textContent = fileNode.name;
    rowButton.append(nameNode);

    rowButton.addEventListener("click", () => {
      void selectPath(fileNode.path);
    });
    return rowButton;
  }

  /**
   * 选中一个路径并按当前视图加载内容。
   * @param {string} repositoryPath 仓库相对路径。
   */
  async function selectPath(repositoryPath) {
    viewState.selectedPath = repositoryPath;
    renderTree();
    await guardAgainstServiceExit(async () => {
      if (viewState.view === DIFF_VIEW) {
        await loadDiffForPath(repositoryPath);
      } else {
        await loadFileContent(repositoryPath);
      }
    });
  }

  /**
   * 加载并渲染单个文件正文。
   * @param {string} repositoryPath 仓库相对路径。
   */
  async function loadFileContent(repositoryPath) {
    const fileResponse = await requestJson(`/api/file?path=${encodeURIComponent(repositoryPath)}`);
    elements.viewerPath.textContent = repositoryPath;
    if (fileResponse.status !== 200) {
      elements.viewerMeta.textContent = "";
      renderNotice(buildNotice({ isFailure: true, title: "无法读取", paragraphs: [fileResponse.body.error] }));
      return;
    }
    const fileBody = fileResponse.body;
    if (fileBody.kind !== "text") {
      elements.viewerMeta.textContent = fileBody.size_label;
      renderNotice(
        buildNotice({
          title: fileBody.kind === "binary" ? "二进制文件" : "文件过大",
          paragraphs: [fileBody.note],
          hint:
            fileBody.kind === "binary"
              ? "二进制文件没有可读正文，查看器不猜测它的内容。"
              : "大文件在浏览器里渲染既慢又难读，请用本地编辑器打开。",
        })
      );
      return;
    }
    elements.viewerMeta.textContent = `${fileBody.language} · ${fileBody.line_count} 行 · ${fileBody.size_label}`;
    elements.statusHint.textContent = fileBody.highlighted
      ? "只读视图 · 服务端语法高亮"
      : "只读视图 · 未安装语法高亮依赖，已降级为纯文本";
    renderCodeLines(fileBody.lines);
  }

  /**
   * 加载并渲染单个文件的逐行改动。
   * @param {string} repositoryPath 仓库相对路径。
   */
  async function loadDiffForPath(repositoryPath) {
    const diffResponse = await requestJson(
      `/api/diff?path=${encodeURIComponent(repositoryPath)}&base=${encodeURIComponent(viewState.baseline)}`
    );
    elements.viewerPath.textContent = repositoryPath;
    if (diffResponse.status !== 200) {
      elements.viewerMeta.textContent = "";
      renderNotice(buildNotice({ isFailure: true, title: "无法读取改动", paragraphs: [diffResponse.body.error] }));
      return;
    }
    const diffBody = diffResponse.body;
    // 头部在空态下会被 renderNotice 清成占位符，所以来源只在有逐行改动时才写头部，
    // 纯重命名那一支交给提示块正文自己说。
    if (diffBody.empty) {
      renderNotice(
        buildNotice(
          // 纯重命名没有逐行改动可看，但它并不是「与当前内容一致」——路径确实变了，
          // 说成「没有改动」会把人引向错误结论。
          diffBody.rename_from
            ? {
                title: "重命名，内容未变",
                paragraphs: [
                  `该文件在该基线下由 <code>${escapeHtmlText(diffBody.rename_from)}</code> 重命名而来，正文没有变化，因此没有逐行改动可看。`,
                ],
                hint: `基线 ${diffBody.base_label}。`,
              }
            : {
                title: "该文件在此基线下没有改动",
                paragraphs: [`基线 ${diffBody.base_label} 与当前内容一致。`],
              }
        )
      );
      return;
    }
    elements.viewerMeta.textContent = diffBody.rename_from
      ? `基线 ${diffBody.base_label} · 重命名自 ${diffBody.rename_from}`
      : `基线 ${diffBody.base_label}`;
    if (diffBody.truncated) {
      elements.statusHint.textContent = "只读视图 · 改动过大，仅显示前若干行";
    }
    renderDiffRows(diffBody.rows);
  }

  /**
   * 渲染带行号的正文；行内容来自服务端已转义的 HTML 片段。
   * @param {string[]} highlightedLines 逐行 HTML。
   */
  function renderCodeLines(highlightedLines) {
    const codeBlock = document.createElement("div");
    codeBlock.className = "code";
    const codeFragment = document.createDocumentFragment();
    highlightedLines.forEach((highlightedLine, lineIndex) => {
      const rowNode = document.createElement("div");
      rowNode.className = "row";
      const lineNumberNode = document.createElement("span");
      lineNumberNode.className = "lineno";
      lineNumberNode.textContent = String(lineIndex + 1);
      const sourceNode = document.createElement("span");
      sourceNode.className = "src";
      // 服务端产出的是 Pygments 转义后的行级 HTML 或转义后的纯文本，不含未转义的源码字符。
      sourceNode.innerHTML = highlightedLine;
      rowNode.append(lineNumberNode, sourceNode);
      codeFragment.append(rowNode);
    });
    codeBlock.append(codeFragment);
    elements.viewerBody.replaceChildren(codeBlock);
  }

  /**
   * 渲染逐行 diff。
   * @param {Array<{kind: string, old_no: number|null, new_no: number|null, text: string}>} diffRows 逐行改动。
   */
  function renderDiffRows(diffRows) {
    const codeBlock = document.createElement("div");
    codeBlock.className = "code diff";
    const codeFragment = document.createDocumentFragment();
    for (const diffRow of diffRows) {
      const rowNode = document.createElement("div");
      rowNode.className = `row ${diffRow.kind}`;
      if (diffRow.kind === "hunk") {
        rowNode.textContent = diffRow.text;
        codeFragment.append(rowNode);
        continue;
      }
      const lineNumberNode = document.createElement("span");
      lineNumberNode.className = "lineno";
      lineNumberNode.append(
        document.createTextNode(diffRow.old_no === null ? "" : String(diffRow.old_no)),
        document.createElement("em"),
        document.createTextNode(diffRow.new_no === null ? "" : String(diffRow.new_no))
      );
      const sourceNode = document.createElement("span");
      sourceNode.className = "src";
      sourceNode.textContent = diffRow.text;
      rowNode.append(lineNumberNode, sourceNode);
      codeFragment.append(rowNode);
    }
    codeBlock.append(codeFragment);
    elements.viewerBody.replaceChildren(codeBlock);
  }

  /**
   * 切换视图。
   * @param {string} nextView 目标视图。
   */
  async function switchView(nextView) {
    if (viewState.isDisconnected || viewState.view === nextView) {
      return;
    }
    viewState.view = nextView;
    viewState.selectedPath = "";
    renderViewTabs();
    if (nextView === DIFF_VIEW) {
      await loadChangedFiles();
    } else {
      elements.statusHint.textContent = "";
      renderTree();
      renderPlaceholder();
    }
  }

  elements.tabFiles.addEventListener("click", () => {
    void switchView(FILES_VIEW);
  });
  elements.tabDiff.addEventListener("click", () => {
    void switchView(DIFF_VIEW);
  });
  elements.baselineSelect.addEventListener("change", () => {
    viewState.baseline = elements.baselineSelect.value;
    viewState.selectedPath = "";
    void loadChangedFiles();
  });
  elements.filterInput.addEventListener("input", () => {
    viewState.filterText = elements.filterInput.value;
    renderTree();
  });
  window.document.addEventListener("keydown", (keyboardEvent) => {
    if (keyboardEvent.target === elements.filterInput) {
      if (keyboardEvent.key === "Escape") {
        elements.filterInput.blur();
      }
      return;
    }
    if (keyboardEvent.key === "f") {
      void switchView(FILES_VIEW);
    } else if (keyboardEvent.key === "d") {
      void switchView(DIFF_VIEW);
    } else if (keyboardEvent.key === "/") {
      keyboardEvent.preventDefault();
      elements.filterInput.focus();
    }
  });

  void initializeViewer();
})();
