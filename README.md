# XJTLU 期末考试卷下载器

从 XJTLU ETD 系统批量下载期末考试卷 PDF 的跨平台工具。

> 🎓 专为西交利物浦大学学生设计，帮助快速下载历年期末考试真题进行复习备考。

## 功能特点

- 📝 **期末考试卷下载**：支持从 XJTLU ETD 系统下载历年期末试卷
- 🚀 **批量处理**：支持同时添加多个试卷链接进行下载
- 📂 **目录管理**：统一选择保存目录，自动处理文件名冲突
- 🖥️ **跨平台支持**：支持 Windows、macOS 和 Linux
- 📊 **进度追踪**：直观的总进度显示
- 🛡️ **智能文件名**：自动根据记录 ID 生成文件名，并避免覆盖
- 🌐 **浏览器自动化**：使用 Playwright 绕过 IP 验证限制

## 快速开始

### Windows

```bash
# 安装 (双击或命令行运行)
install_win.bat

# 运行 (双击或命令行运行)
run_win.bat
```

### macOS

```bash
# 安装
chmod +x install_mac.sh
./install_mac.sh

# 运行
chmod +x run_mac.sh
./run_mac.sh
```

### Linux

```bash
# 安装
chmod +x install_linux.sh
./install_linux.sh

# 运行
chmod +x run_linux.sh
./run_linux.sh
```

## 手动安装

### 依赖要求

- Python 3.8+
- Tkinter (Linux 需手动安装)

### 安装步骤

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 安装 Playwright 浏览器
python -m playwright install chromium

# 3. (Linux) 安装系统依赖
python -m playwright install-deps chromium
```

## 使用方法

1. **启动程序**：运行对应平台的脚本或 `python main.py`

2. **添加任务**：
   - 点击 "➕ Add URL" 按钮增加输入框
   - 将浏览器中的 PDF Viewer URL 粘贴到输入框中
   - 支持粘贴多个不同文档的链接

3. **设置保存位置**：
   - 点击 "📂 Browse..." 选择文件保存的目标文件夹

4. **开始下载**：
   - 点击 "🚀 Start Batch Download"
   - 程序将自动处理所有链接并将文件保存到指定目录

## URL 格式示例

程序支持如下格式的 URL：

```
https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3F...
```

## 项目结构

```
XJTLU_Final_paper_PDF_downloader/
├── main.py              # GUI 主程序
├── downloader.py        # Playwright 下载核心
├── url_parser.py        # URL 解析器
├── test_download.py     # 命令行测试脚本
├── requirements.txt     # Python 依赖
├── install_win.bat      # Windows 安装脚本
├── install_mac.sh       # macOS 安装脚本
├── install_linux.sh     # Linux 安装脚本
├── run_win.bat          # Windows 运行脚本
├── run_mac.sh           # macOS 运行脚本
├── run_linux.sh         # Linux 运行脚本
└── README.md            # 说明文档
```

## 注意事项

⚠️ **重要提示**：

1. 需要先在 XJTLU ETD 网站上找到试卷，然后复制 PDF 查看器的 URL
2. URL 中包含时效性签名，请在有效期内及时下载
3. 下载请求的 IP 必须与获取链接时的 IP 一致（请使用校园网或同一网络）
4. 本工具仅供 XJTLU 学生学习复习使用

## 如何获取试卷链接

1. 访问 [XJTLU ETD 系统](https://etd.xjtlu.edu.cn/)
2. 搜索你需要的课程期末试卷
3. 点击查看 PDF，在浏览器地址栏复制完整 URL
4. 将 URL 粘贴到本程序中下载

## 技术栈

- Python 3.8+
- Tkinter (跨平台 GUI)
- Playwright (浏览器自动化)

## License

MIT License
