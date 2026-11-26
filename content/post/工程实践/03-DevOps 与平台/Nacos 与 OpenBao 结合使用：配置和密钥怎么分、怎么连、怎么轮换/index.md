---
title: Nacos 与 OpenBao 结合使用：配置和密钥怎么分、怎么连、怎么轮换
description: Nacos 管普通配置，OpenBao 管密码和密钥。结合 Agent 与 Dokploy 两种接入方式，说明启动顺序、变更与轮换，以及生产迁移中的值保真、Compose 转义、持久化网络、恢复演练和凭据交付。
date: 2026-11-20T18:00:00+08:00
lastmod: 2026-11-26
slug: nacos-openbao-together
image: images/index/index.svg
categories:
    - 工程实践
tags:
    - DevOps 与平台
    - Nacos
    - OpenBao
    - 配置中心
    - 密钥管理
draft: false
---

前两篇分别讲了 [Nacos](/p/config-center-service-discovery-nacos/) 和 [OpenBao](/p/openbao-secrets-dynamic-deployments/)。两篇都提到同一个分工：普通配置放 Nacos，密钥放 OpenBao。但真正落地时，问题往往出在两者的接缝处：

- 数据库地址放 Nacos，密码放 OpenBao，应用怎么把它俩拼起来？
- 应用连 Nacos 也要密码，这个密码又放哪？
- 改了一个开关、轮换了一个密码，分别要做什么？
- 其中一个挂了，应用还能不能跑？

分工是：**Nacos 保存普通配置，OpenBao 保存密钥，包括应用读取 Nacos 的密码。** 密钥可以由 OpenBao Agent 渲染给应用，也可以由已有部署平台在发布时注入。前者适合持续渲染文件，后者可复用现有发布流程；两种方式都要明确新值何时到达消费者。

## 一、先判断：一项值该放哪边

先判断一个值是否直接授予访问能力，泄露后是否需要更换。密码、Token、私钥以及携带这些内容的连接串，都应按密钥管理。普通配置仍可能暴露内部拓扑或业务策略，需要控制读取权限。

| 值 | 放哪 | 说明 |
| --- | --- | --- |
| 日志级别、功能开关、限流阈值、超时时间 | Nacos | 按业务需要调整，可见范围仍按内部数据管理 |
| 数据库地址、端口、库名、用户名 | Nacos | 是连接信息，不是凭据；单独泄露不能登录 |
| 数据库密码、Redis 密码 | OpenBao | 泄露必须改密码 |
| 第三方 API Key、支付密钥、邮件服务 Token | OpenBao | 泄露可能直接造成损失 |
| 私钥、签名密钥、JWT 签名密钥 | OpenBao | 最高价值，还要考虑轮换窗口 |
| 带密码的连接串，如 `postgres://user:pass@host/db` | OpenBao，或按应用契约拆分 | 整串属于密钥；已支持分字段读取时，也可只将密码放 OpenBao |
| 带签名参数的 Webhook URL | OpenBao | 整条 URL 本身就是凭据 |
| 第三方服务的公开地址、回调路径 | Nacos | 公开信息 |

容易出错的是「带凭据的连接串」：整串放进 Nacos，会把密码交给普通配置的读者。已有应用只接受完整连接串时，可先把整串原样迁入 OpenBao；拆分字段属于后续应用改造，单独验证连接池和编码行为。

## 二、整体结构：谁连谁

![应用启动时依次从 OpenBao 和 Nacos 取值的流程](images/index/startup-flow.svg)

*图 1：Agent 先用 AppRole 登录 OpenBao，把应用的密钥（包括 Nacos 密码）渲染成本地文件；应用读这个文件，再用其中的 Nacos 密码读取普通配置，最后把配置中的引用替换成真实密钥。*

四个参与者各管一件事：

| 组件 | 职责 | 不做的事 |
| --- | --- | --- |
| OpenBao | 保存密钥、按策略授权、记录审计日志 | 不保存普通配置，不推送配置变更 |
| OpenBao Agent | 在应用所在机器上登录 OpenBao、续期 token、把密钥渲染成文件 | 不读 Nacos |
| Nacos | 保存普通配置和密钥引用，配置变更时通知应用 | 不保存密钥的值 |
| 应用 | 读密钥文件和 Nacos 配置，把引用替换成真实值 | 不在日志或接口里输出密钥 |

这里选了 Agent 渲染文件的方式，因为它对应用的改动最小：应用不需要接 OpenBao SDK，也不用自己处理登录、续期和重试。如果应用已经直接调用 OpenBao API，下文的思路同样适用，只是读密钥的那一步换成 API 调用。其他接入方式见 [OpenBao 那篇第四节](/p/openbao-secrets-dynamic-deployments/)。

## 三、Nacos 自己的密码放哪

应用连 Nacos 需要用户名和密码。如果这个密码仍由人手工填入并分发 `.env`，就要另外维护它的来源和更新。部署平台生成的受限环境文件可以作为交付载体，源头仍由 OpenBao 统一管理。

做法是**把 Nacos 的读取账号也当作一个密钥，交给 OpenBao 保管**：

```text
OpenBao 路径                       内容
kv/prod/project-a/runtime          DATABASE_PASSWORD、PAYMENT_API_KEY ...
kv/prod/project-a/nacos            password（project-a 在 Nacos 的只读账号密码）
```

在下文的 Agent 方案中，机器预先取得 AppRole 的 RoleID 和一次性 SecretID，其余凭据从 OpenBao 来。一次性 SecretID 消费后，再次认证需要可信流程下发新材料，自动续期也有权限和寿命边界。信任链如下：

```text
可信的部署流程 → AppRole 登录 OpenBao → 拿到 Nacos 密码和业务密钥 → 读 Nacos 配置
```

Nacos 地址、命名空间、用户名这些不敏感的值，可以继续用环境变量传给应用。

OpenBao 的引导信息要能独立取得。把它的地址或 AppRole 信息放在 Nacos 里，会形成启动依赖环；初始化和恢复时两边都可能无法取得所需材料。

## 四、在 Nacos 里引用 OpenBao 的密钥

Nacos 配置里需要用到密钥的地方，只写一个引用，不写值。本文的约定是：**字段名以 `_ref` 结尾，值是密钥文件里的键名**。

```yaml
# Nacos：namespace=prod，group=project-a，dataId=api.yaml
log_level: info
feature_flags:
  new_checkout: false
database:
  host: db.internal.example
  port: 5432
  name: project_a
  user: project_a_app
  password_ref: DATABASE_PASSWORD   # 真实值在 OpenBao，由 Agent 渲染到密钥文件
payment:
  endpoint: https://pay.example.com/api
  api_key_ref: PAYMENT_API_KEY
```

这样做的好处：

- 能读 Nacos 的人，只能看到「这里要用一个数据库密码」，看不到密码本身。
- 配置里能看出每项密钥被谁用，排查和审计时可以顺着引用找到 OpenBao 的路径。
- 引用写错了，应用启动时就会因为找不到键而失败，而不是带着空密码跑起来。

引用写键名还是写完整路径，取决于应用怎么读密钥：

| 读取方式 | 引用写法 | 说明 |
| --- | --- | --- |
| Agent 渲染文件（本文） | `DATABASE_PASSWORD` | 路径写在 Agent 模板里，应用只认键名 |
| 应用直接调用 OpenBao API | `kv/prod/project-a/runtime#DATABASE_PASSWORD` | 应用按路径和字段自己去取 |

两种都可以，团队需统一消费者使用的约定，并明确引用字段的命名规则，方便检查 Nacos 是否混入明文密钥。

## 五、落地示例：一台机器上的 Python 服务

下面以一个 Python 服务 `project-a` 为例，用 systemd 或 Docker Compose 部署都可以。示例中的地址和名称都是虚构的。

### 1. OpenBao：路径和策略

在 OpenBao 中写入两条记录：`kv/prod/project-a/runtime` 和 `kv/prod/project-a/nacos`。然后给 `project-a` 的生产环境身份一条只读策略：

```hcl
# policy: app-project-a-prod
path "kv/data/prod/project-a/runtime" {
  capabilities = ["read"]
}

path "kv/data/prod/project-a/nacos" {
  capabilities = ["read"]
}
```

策略里写的是 KV v2 的 API 路径（带 `data/`），不要漏掉。把策略绑定到一个 AppRole 上，比如 `project-a-prod`。AppRole 的引导材料怎样安全送到机器上，见 [OpenBao 那篇第三节](/p/openbao-secrets-dynamic-deployments/)。

### 2. OpenBao Agent：登录并渲染密钥文件

Agent 配置（OpenBao 2.7 的写法；连接服务器的块名仍然是 `vault`）：

```hcl
# /etc/openbao-agent/project-a.hcl
vault {
  address = "https://openbao.internal.example:8200"
  ca_cert = "/etc/openbao-agent/ca.crt"
}

auto_auth {
  method {
    type = "approle"
    config = {
      role_id_file_path   = "/etc/openbao-agent/project-a/role_id"
      secret_id_file_path = "/etc/openbao-agent/project-a/secret_id"
      # 默认读取后删除 secret_id 文件，减少它在磁盘上停留的时间
    }
  }
}

template_config {
  # KV v2 的值不会主动推送变化，Agent 按这个间隔重新读取，默认 5m
  static_secret_render_interval = "5m"
}

template {
  source               = "/etc/openbao-agent/project-a/secrets.env.ctmpl"
  destination          = "/run/project-a/secrets.env"
  perms                = "0400"
  error_on_missing_key = true
}
```

模板文件把两条记录渲染成 `键=值` 格式：

```text
{{- with secret "kv/data/prod/project-a/runtime" }}
DATABASE_PASSWORD={{ .Data.data.DATABASE_PASSWORD }}
PAYMENT_API_KEY={{ .Data.data.PAYMENT_API_KEY }}
{{- end }}
{{- with secret "kv/data/prod/project-a/nacos" }}
NACOS_PASSWORD={{ .Data.data.password }}
{{- end }}
```

用 `bao agent -config=/etc/openbao-agent/project-a.hcl` 启动 Agent，建议交给 systemd 管理，并让应用服务依赖它启动。注意三点：

- `/run` 是内存文件系统，机器重启后文件消失，由 Agent 重新生成，密钥不会长期落盘。
- 文件权限 `0400`，Agent 和应用应使用同一个专用系统用户，或者通过用户组只让应用可读。
- `error_on_missing_key = true` 让字段缺失时直接报错，避免渲染出空值。

### 3. 应用：先读密钥，再读 Nacos，最后替换引用

Nacos 客户端沿用 [Nacos 那篇](/p/config-center-service-discovery-nacos/) 的 `nacos-sdk-python` v3 写法：

```python
import asyncio
import os
from pathlib import Path

import yaml
from v2.nacos import ClientConfigBuilder, ConfigParam, NacosConfigService

SECRETS_FILE_PATH = Path(os.getenv("SECRETS_FILE", "/run/project-a/secrets.env"))


def load_rendered_secrets(secrets_file_path: Path) -> dict[str, str]:
    """读取 Agent 渲染的 键=值 文件。"""
    rendered_secrets_dict: dict[str, str] = {}
    for line in secrets_file_path.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            key, _, value = line.partition("=")
            rendered_secrets_dict[key] = value
    return rendered_secrets_dict


def resolve_secret_refs(config_node, rendered_secrets_dict: dict[str, str]):
    """把 xxx_ref 字段替换成 xxx，值从密钥文件中取。"""
    if not isinstance(config_node, dict):
        return config_node
    resolved_config_dict = {}
    for key, value in config_node.items():
        if key.endswith("_ref"):
            # 找不到键时抛出 KeyError，让应用启动失败，而不是带着空密码运行
            resolved_config_dict[key.removesuffix("_ref")] = rendered_secrets_dict[value]
        else:
            resolved_config_dict[key] = resolve_secret_refs(value, rendered_secrets_dict)
    return resolved_config_dict


async def load_settings() -> dict:
    rendered_secrets_dict = load_rendered_secrets(SECRETS_FILE_PATH)
    nacos_client_config = (
        ClientConfigBuilder()
        .server_address(os.environ["NACOS_SERVER_ADDR"])
        .namespace_id(os.environ["NACOS_NAMESPACE"])
        .username(os.environ["NACOS_USERNAME"])
        .password(rendered_secrets_dict["NACOS_PASSWORD"])
        .build()
    )
    config_client = await NacosConfigService.create_config_service(nacos_client_config)
    raw_config_text = await config_client.get_config(
        ConfigParam(data_id="api.yaml", group="project-a")
    )
    return resolve_secret_refs(yaml.safe_load(raw_config_text), rendered_secrets_dict)


settings_dict = asyncio.run(load_settings())
# settings_dict["database"]["password"] 已是真实密码；不要打印 settings_dict
```

环境变量里只剩不敏感的三项：

```env
NACOS_SERVER_ADDR=https://nacos.internal.example
NACOS_NAMESPACE=prod
NACOS_USERNAME=project-a-reader
```

替换后的配置对象含有真实密钥，打日志、做健康检查接口、报错上报时都不要整体输出它。

这里的模板与解析器只演示单行键值文件。多行密钥、特殊字符或不同 dotenv 消费者，需要按目标格式编码并测试，不能把任意值直接拼接成环境文件。

### 4. 已有 Dokploy 时，可在部署阶段取得密钥

如果已有平台支持 OpenBao 兼容的 KV 读取，可以先复用发布流程。部署平台用专用身份读取业务密钥和 Nacos 密码，生成受限环境文件，再创建应用容器；应用继续通过自己的配置入口读取 Nacos。这条路径可以保留现有业务代码的配置契约。

![部署平台读取 OpenBao、Compose 创建容器、应用读取 Nacos 的数据流](images/index/deployment-flow.svg)

*图 2：Dokploy Provider 模式的架构示意。密钥在发布时注入，应用启动后读取 Nacos；它不包含 Agent 自动渲染与续期的承诺。*

这里需要单独维护 Provider 身份的权限、来源限制和到期时间。AppRole 用于签发 token，不代表 Provider 已经具备 AppRole 自动登录与续期能力。Nacos 的密钥引用也需要消费者解析，不能仅凭 `_ref` 字段命名就自动生效。

在核对过的 Dokploy v0.31.0 中，平台生成环境文件时会处理引号、反斜杠和部分美元符号。升级前后都要沿真实发布链路检查最终值，不能照搬别的 dotenv 写法。[环境文件生成源码](https://github.com/Dokploy/dokploy/blob/v0.31.0/packages/server/src/utils/docker/utils.ts)

## 六、变化怎么传递

两边的变化走不同的路径，生效方式也不同：

| 变化 | 在哪改 | 怎么到达应用 | 何时生效 |
| --- | --- | --- | --- |
| 改开关、阈值、日志级别 | Nacos | Nacos 推送变更，应用的监听回调重新加载 | 秒级，取决于应用是否支持热更新 |
| 改数据库地址等连接信息 | Nacos | 同上，但需要重建连接池 | 应用重建对象或重启后 |
| 轮换业务密钥 | OpenBao | Agent 按间隔重新读取并渲染文件 | 最长等一个渲染间隔，再加应用重新加载的时间 |
| 轮换 Nacos 读取密码 | OpenBao 和 Nacos 两边 | 同上 | 见下方步骤 |
| 发布时注入的密钥更新 | OpenBao | 部署平台在下一次发布时重新读取并创建容器 | 完成重新发布后，按实际消费者验证 |

监听 Nacos 配置变更的写法见 [Nacos 那篇第六节](/p/config-center-service-discovery-nacos/)。注意：**Nacos 配置变了以后，要用当前的密钥文件重新做一次引用替换**，否则新增的 `_ref` 字段会解析失败。

### 密钥轮换：先新增，再切换，最后废弃

数据库密码这类凭据，轮换时不要「先改密码再更新 OpenBao」，那样在两步之间应用会登录失败。安全的顺序是：

1. **新增**：在数据库里创建新密码（或新账号），旧密码暂时保留。
2. **写入 OpenBao**：更新 `kv/prod/project-a/runtime`，KV v2 会保留旧版本，出问题可以回退。
3. **等待生效**：等 Agent 重新渲染文件，再让应用重新加载或重启，确认所有实例都用上了新值。
4. **废弃旧密码**：确认没有实例在用旧密码后，在数据库中删除它。

文件内容变了以后，应用要重新读取才会用上新值。只在启动时读取的应用需要重启，可以在 Agent 的 `template` 里加 `exec` 让它渲染完自动执行重启命令；能热加载的应用可以自己监听文件变化。

Nacos 读取密码的轮换同理：先在 Nacos 里给读取账号设置新密码并保留旧密码（如果 Nacos 版本不支持一个账号同时有两个密码，就新建一个账号，切换完成后再删除旧账号），再更新 OpenBao，等所有实例都切到新密码后，最后删掉旧的。

## 七、任何一方故障时会怎样

下表针对前面的 Agent 文件渲染示例，并假定新实例没有可复用的密钥文件。已有发布时注入环境变量的容器，通常能继续使用已经取得的值；后续发布是否成功还取决于发布平台能否重新读取 OpenBao。

| 故障 | 正在运行的实例 | 新启动或重启的实例 | 怎么减轻 |
| --- | --- | --- | --- |
| Nacos 不可用 | 继续用内存中的配置，收不到变更 | 读不到配置，可能启动失败 | 多数 Nacos 客户端有本地快照，可在故障时使用；上线前实际验证一次 |
| OpenBao 不可用或处于封存状态 | 继续运行，密钥文件还在 | Agent 渲染不出文件，应用无法启动；也无法轮换 | 准备好解封流程和解封材料的保管方式；重要服务考虑高可用部署 |
| Agent 停止 | 继续运行，文件内容停在最后一次渲染 | 拿不到新文件 | 用 systemd 自动重启 Agent，并监控它的状态 |
| 两者都不可用 | 继续运行 | 无法启动 | 这时不要重启实例，等依赖恢复 |

采用 Shamir 人工解封时，OpenBao 进程重启后需要达到门限的原始解封材料。机器意外重启后，重新获取密钥的消费者会受影响；明确解封责任和材料保管方式。使用自动解封时，还要维护外部 KMS 等依赖的可用性和恢复路径。[封存与解封](https://openbao.org/docs/concepts/seal/)

## 八、命名和权限对齐

两边的命名用同一套规则，一眼就能对应起来，也方便写脚本检查：

| 层级 | Nacos | OpenBao | 例子 |
| --- | --- | --- | --- |
| 环境 | namespace | 路径第一段 | `prod` ↔ `kv/prod/...` |
| 应用 | group | 路径第二段 | `project-a` ↔ `kv/prod/project-a/...` |
| 内容 | dataId | 路径第三段 | `api.yaml` ↔ `kv/prod/project-a/runtime` |
| 应用的身份 | 只读账号 `project-a-reader` | AppRole `project-a-prod` + 策略 `app-project-a-prod` | 每个应用每个环境一个，不共用 |

权限也要对齐：

- 应用在 Nacos 只能读自己的 namespace 和 group，在 OpenBao 只能读自己的路径。
- 改 Nacos 配置的人，不一定能读 OpenBao 的密钥；反过来也一样。
- 能同时改两边、还能触发部署的人或自动化流程，权限最大，人数要最少，操作要留记录。

## 九、常见反模式

- **连接串混放**：把带密码的连接串放进 Nacos，会暴露给普通配置读者。整串放 OpenBao，或在应用支持时拆分。
- **读取密码硬编码**：密码写死在镜像或手工分发的 `.env` 里，多了一份难以追踪和轮换的源头。统一由 OpenBao 提供，生成文件继续限制权限。
- **应用身份共用**：所有应用共用一个 token 或 Nacos 账号，会扩大单个应用被攻破后的影响范围。
- **引导循环依赖**：OpenBao 依赖 Nacos 提供地址或凭据，初始化和恢复时两边都可能无法取得材料。
- **输出完整配置**：替换引用后的配置里有真实密钥，一打印就进入日志系统。
- **提前废弃旧密码**：在 OpenBao 更新和应用重载之间，应用可能登录失败。先切换消费者再废弃旧凭据。
- **忽略加载时机**：Agent 有渲染间隔，发布时注入则需要重新发布，应用也要按自身机制重新加载。

## 十、落地顺序

不需要一次改完所有应用，可以按这个顺序推进：

1. **盘点**：把现有 `.env` 里的每一项按第一节的表分类，标出要放 OpenBao 的值。
2. **约定**：定好两边的命名规则和 `_ref` 引用写法。
3. **先迁一个应用**：给它建 OpenBao 路径、策略、AppRole 和 Nacos 只读账号，部署 Agent，改造启动代码。
4. **演练故障**：分别停掉 Nacos、封存 OpenBao、停掉 Agent，确认第七节表格里的行为和预期一致。
5. **演练轮换**：按第六节轮换一次数据库密码和 Nacos 读取密码。
6. **检查配置**：发布前核对普通配置是否混入凭据；配置量较大时可辅助扫描，结合字段含义判断。
7. **推广**：其他应用沿已验证的方式迁移，确认新来源生效后清理旧的手工密钥副本，保留必要的生成文件和恢复材料。

## 十一、生产迁移还需要核对什么

测试环境能读取新配置，是生产切换的一个前置信号。生产还有旧密码的精确值、既有覆盖关系、发布平台的环境文件和真实用户会话。迁移时先固定这些基线，后面的检查才有明确的比较对象。

![冻结配置基线、验证实际注入、演练隔离恢复、检查生产业务入口的迁移过程](images/index/migration-checkpoints.svg)

*图 3：生产迁移的验证顺序示意。配置预检、恢复演练和真实业务调用分别证明不同边界，流程图本身不属于验收证据。*

### 从旧容器收到的值开始比较

完整连接串、签名密钥、Provider 加密密钥和密码哈希，都有依赖现有数据的消费者。迁移这些值时先保持原值，密码轮换和应用升级另开变更。比较时也要区分空字符串、变量未设置和应用默认值；只检查字段存在，可能漏掉真正生效的值已经变化。

一次实际迁移预检中，Compose 展示结果里的美元符号比旧容器更多，但通过真实 Compose 创建的临时容器收到的值与旧容器一致。若根据展示文本回头改 OpenBao，反而会改变正确的密码。处理这类问题时，在内存中比较最终容器值，只报告通过状态；再通过真实管理端登录验证密码处理链路。[Compose 插值规则](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)

### 把临时连通改成可重建的部署

手工把容器连接到网络后，网页可能立即恢复，但部署定义仍需记录这条连接。将共享网络接入和唯一别名写回 Compose，代理通过别名访问上游，再按维护范围重建并复测。数据库继续留在独立内部网络，避免为了入口连通而扩大暴露范围。[Compose 网络声明](https://docs.docker.com/reference/compose-file/networks/)

使用来源绑定的 token 时，还要确认真正的发布进程从哪里访问 OpenBao。代理层白名单、OpenBao 受信任代理与 token 的来源限制是相邻边界；验证发布进程可读、其他来源被拒绝，同时核对转发头不能绕过限制。共享代理网段也意味着需要信任这个网段中的其他成员。

### 用恢复后的读回结果验收备份

将 SQL 备份恢复到独立数据库后核对表数据，将 Raft 快照恢复到独立 OpenBao 后用原始材料解封，再登录读取目标记录。演练使用独立卷和临时目录，结束后移除自己创建的资源。

在一次 OpenBao 2.7.2 演练中，源实例采用 3 份解封材料、门限 2，临时实例按 1 份、门限 1 初始化后解封失败；按源参数重建临时实例后恢复通过。这个观察提醒我们记录版本、seal 类型、份额和门限。强制恢复会跳过快照密钥一致性检查，仍然需要原数据对应的解封材料，具体流程按版本核对。[Raft 快照恢复](https://openbao.org/docs/api/system/storage/raft/)

### 交付中同时记录账号、到期与保管状态

服务入口、用户名、凭据引用、权限、到期时间和恢复材料位置，应随部署完成登记。个人登录会话、应用发布身份和应急解封材料分别管理；记录了 token 到期日，也需要说明是否已有提醒和轮换执行流程。

临时回滚归档在约定验证完成后清理，日常凭据和解封材料继续保管。如果临时文件被打包进其他备份，清理时也要核对这些副本。备份与所有可用解密私钥都在同一台电脑时，电脑丢失仍会造成恢复缺口；如实记录本机副本、异机副本和恢复私钥的保管状态。

## 总结

接入方式取决于现有应用的加载契约和发布能力。已有部署平台时，先复用发布阶段的密钥注入；需要持续渲染或动态凭据时，再评估 Agent。下一步可以从一个应用开始，冻结旧配置，走完实际注入、隔离恢复和真实业务调用，再把验证过的步骤维护进运维手册。

## 参考资料

- [OpenBao Agent](https://openbao.org/docs/agent-and-proxy/agent/)
- [OpenBao Agent 模板](https://openbao.org/docs/agent-and-proxy/agent/template/)
- [OpenBao Agent AppRole 方法](https://openbao.org/docs/agent-and-proxy/autoauth/methods/approle/)
- [OpenBao KV v2](https://openbao.org/docs/secrets/kv/kv-v2/)
- [OpenBao 封存与解封](https://openbao.org/docs/concepts/seal/)
- [Nacos 配置管理概览](https://www.nacos.io/en/docs/v3.2/manual/user/config/overview/)
- [Nacos 配置加密插件](https://www.nacos.io/en/docs/v3.2/plugin/config-encryption-plugin/)
- [nacos-sdk-python](https://github.com/nacos-group/nacos-sdk-python)
- [Docker Compose 环境变量插值](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/)
- [Docker Compose 网络](https://docs.docker.com/reference/compose-file/networks/)
- [OpenBao Raft 快照 API](https://openbao.org/docs/api/system/storage/raft/)
- [Dokploy v0.31.0 环境文件生成实现](https://github.com/Dokploy/dokploy/blob/v0.31.0/packages/server/src/utils/docker/utils.ts)

2026-11-26 补充部署平台注入与生产迁移经验；涉及版本行为的判断限于文中标注的实现，示例名称与地址均已脱敏。
