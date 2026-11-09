# Nova AI 智能工作台

项目基于 FastAPI、原生 HTML/CSS/JavaScript 和 SQLite。现有架构保持不变。

## 启动

```bash
cd my-ai-platform
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

浏览器访问：http://127.0.0.1:8001

## 账户功能

- 登录：`POST /auth/login`
- 注册：`POST /auth/register`
- 当前用户：`GET /auth/me`
- 退出：`POST /auth/logout`
- 注册成功后自动登录，有效期 12 小时。
- 注册账号固定为普通用户，不能自行注册管理员。
- 用户名需为 3-32 位小写字母、数字或下划线。
- 密码需为 8-128 位，并同时包含字母和数字。
- 密码使用 PBKDF2-SHA256 加盐保存，不保存明文密码。

注册请求示例：

```json
{
  "username": "new_user",
  "password": "Password123",
  "display_name": "新用户"
}
```

## 初始账号

| 账号 | 密码 | 权限 |
| --- | --- | --- |
| `admin` | `Admin@123456` | 管理员 |
| `zhangsan` | `Student@123` | 普通用户 |
| `lisi` | `Student@123` | 普通用户 |
| `wangwu` | `Student@123` | 普通用户 |

正式部署前请修改初始密码。

## 数据库

数据库文件是 `platform.db`，由后端自动初始化，包含：

- `users`：账号、加盐密码摘要、姓名、角色、启用状态。
- `sessions`：登录令牌和过期时间。
- `activity_logs`：每位用户的功能调用、状态、耗时和内容摘要。

管理员登录后可在“后台数据”标签页查看账号汇总和最近请求。

## AI 与文件接口

| 功能 | 路由 | 请求 |
| --- | --- | --- |
| 简历优化 | `POST /resume` | JSON `{text, provider?}` |
| 文案生成 | `POST /copywrite` | JSON `{scene, provider?}` |
| 翻译助手 | `POST /translate` | JSON `{text, provider?}` |
| PDF 摘要 | `POST /pdf-summary` | multipart `file` |
| CSV 分析 | `POST /csv-preview` | multipart `file` |

所有工具接口都需要在 `X-Session-Token` 请求头中携带登录令牌。

## 主要文件

- `main.py`：FastAPI、注册登录、权限、SQLite、AI 和文件接口。
- `index.html`：登录、注册、AI 工具和管理员后台界面。
- `platform.db`：用户、会话和使用记录数据。
- `requirements.txt`：Python 依赖。
- `.env`：AI 服务密钥，请勿提交或公开。

## Automated tests

Use Python 3.12:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Each test uses a temporary SQLite database. Model calls are mocked: the tests check API behaviour, authentication, permissions, upload validation and activity logging, not the quality of a live model's answers. No API key is required.

## Docker

```sh
docker build -t nova-ai:local .
docker run --rm --name nova-ai -p 127.0.0.1:8000:8000 -v nova-data:/data nova-ai:local
```

Open http://localhost:8000. The named volume preserves the database. To enable live model requests, add `--env-file .env` before the image name; keep that file private. Only the application, HTML and dependency list enter the build context. The image runs as a non-root user and includes a health check.

This is a local demonstration application with seeded demonstration accounts. Keep it bound to localhost; public deployment requires replacing the demonstration account setup and reviewing the application configuration.

## Continuous integration

[GitHub Actions](https://github.com/kevhsx/AI-nova/actions) runs the API tests and builds and starts the Docker image on pushes and pull requests. The Docker job checks `/health`; the test job retains a JUnit report. A green run confirms these checks, not live AI quality or cloud deployment.
