# 如何发布 AgentGuard Python SDK 到 PyPI

## 前提条件

1. 注册 PyPI 账号: https://pypi.org/account/register/
2. 生成 API Token: https://pypi.org/manage/account/token/
3. 安装发布工具:
```bash
pip install build twine
```

## 发布步骤

### 1. 更新版本号和项目信息

编辑 `pyproject.toml`:
- 修改 `version` 为新版本号
- 更新 `authors` 中的真实信息
- 更新 `project.urls` 中的实际仓库地址

### 2. 构建分发包

```bash
cd agentguard-sdk-python
python -m build
```

这会在 `dist/` 目录生成:
- `agentguard_zhx-1.0.0-py3-none-any.whl` (wheel包)
- `agentguard-zhx-1.0.0.tar.gz` (源码包)

### 3. 检查包

```bash
twine check dist/*
```

### 4. 上传到 TestPyPI (可选,用于测试)

```bash
twine upload --repository testpypi dist/*
```

测试安装:
```bash
pip install --index-url https://test.pypi.org/simple/ agentguard-zhx
```

### 5. 上传到正式 PyPI

```bash
twine upload dist/*
```

输入你的 PyPI 用户名和 API Token。

### 6. 验证安装

```bash
pip install agentguard-zhx
```

## 注意事项

1. **包名已更改为 `agentguard-zhx`**
2. 每次发布新版本前,必须更新 `pyproject.toml` 中的版本号
3. 已发布的版本无法删除或覆盖,只能发布新版本
4. 建议先发布到 TestPyPI 测试,确认无误后再发布到正式 PyPI

## 使用 GitHub Actions 自动发布 (推荐)

创建 `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

在 GitHub 仓库设置中添加 Secret: `PYPI_API_TOKEN`

## 更新文档

发布后,更新 README.md 中的安装命令:
```bash
pip install agentguard-zhx
```
