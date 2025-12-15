# XJTLU PDF 批量下载器

从 XJTLU ETD (Electronic Theses and Dissertations) 系统批量下载 PDF 文件的工具。

## 功能特点

- 🚀 **批量处理**：支持同时添加多个 PDF 链接进行下载
- 📂 **目录管理**：统一选择保存目录，自动处理文件名冲突
- 🖥️ **动态界面**：可动态添加/删除下载任务
- 📊 **进度追踪**：直观的总进度显示
- 🛡️ **智能文件名**：自动根据记录 ID 生成文件名，并避免覆盖

## 安装

1. 确保已安装 Python 3.8+

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. **添加任务**：
   - 点击 "➕ 添加 URL" 按钮增加输入框
   - 将浏览器中的 PDF Viewer URL 粘贴到输入框中
   - 支持粘贴多个不同文档的链接

3. **设置保存位置**：
   - 点击 "📂 浏览..." 选择文件保存的目标文件夹

4. **开始下载**：
   - 点击 "🚀 开始批量下载"
   - 程序将自动处理所有链接并将文件保存到指定目录

## URL 格式示例

程序支持如下格式的 URL：

```
https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3F...
```

## 注意事项

⚠️ **重要提示**：

1. URL 中包含时效性签名，请在有效期内及时下载
2. 本工具仅供学习研究使用

## 技术栈

- Python 3.8+
- Tkinter (GUI)
- Requests (HTTP 下载)
