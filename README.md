# XJTLU 期末考试卷下载器

从 XJTLU ETD 系统批量下载期末考试卷 PDF 的跨平台工具。

> 🎓 专为西交利物浦大学学生设计，帮助快速下载历年期末考试真题进行复习备考。

## 问题背景 ❓

XJTLU ETD 系统只允许在线查看 PDF 试卷，**不提供直接下载功能**。这导致：
- 🔒 无法离线查看试卷，每次都要联网打开
- 📵 网络不稳定时反复加载浪费时间
- 📚 无法批量整理和存档历年真题
- 😤 想打印复习使用但不能保存本地

**本工具通过浏览器自动化技术，安全合法地解决这一问题！** ✨

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

## 系统兼容性测试状态

| 平台 | 状态 | 说明 |
|------|------|------|
| **Windows** | ✅ 已测试 | 在 Windows 系统上进行了实机测试，功能正常 |
| **macOS** | ⚠️ 未测试 | 代码支持 macOS，但未在实机上测试过。如有问题请反馈 |
| **Linux** | ⚠️ 未测试 | 代码支持 Linux，但未在实机上测试过。如有问题请反馈 |

> 💡 虽然 macOS 和 Linux 版本未进行实机测试，但代码已包含所有必要的跨平台适配（字体、滚轮、路径处理等）。如遇到问题，请在 GitHub Issues 中反馈，我会尽快帮助解决！

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

## 遇到问题？

如果遇到个别复杂问题导致程序无法正常运行，请：

1. **查看错误提示**：程序会用中文详细说明问题原因和解决方案
2. **GitHub Issue**：在[项目 Issues](https://github.com/kevinlasnh/XJTLU_Final_paper_PDF_downloader/issues)中留言描述问题
3. **询问 Agent**：你也可以询问我（Copilot），我会尽力帮助解决

遇事不决，记得先关闭 VPN/梯子/代理再试一次 😄

## License

本项目采用 **AGPL-3.0 + Commercial License** 双重许可模式。

### 🟢 AGPL-3.0 许可（免费，适合开源/学生使用）

**你可以免费使用，前提是：**

✅ **允许的用途：**
- 个人学习和研究
- 教育和学术目的
- 非营利组织
- 开源项目（遵循 AGPL-3.0）

✅ **必须满足的条件：**
1. 保留所有版权声明
2. 公开你的源代码
3. 你的整个项目也必须采用 AGPL-3.0 许可
4. 记录你所做的修改
5. 如果在网络/服务器上运行，必须向用户提供源代码访问权

❌ **不能做的事：**
- 将代码用于闭源应用
- 提供付费服务而不公开源代码
- 在商业产品中使用而不遵循 AGPL-3.0

**详见：** [GNU AGPL-3.0 License](https://www.gnu.org/licenses/agpl-3.0.html)

---

### 🔵 商业许可（需要付费）

**如果你需要以下任一场景，必须获得商业许可证：**

❌ 在闭源应用中使用  
❌ 作为商业产品或服务的一部分  
❌ 提供付费 SaaS/云服务  
❌ 内部业务运营（超过 5 个用户）  
❌ 嵌入硬件或 IoT 设备出售  
❌ 作为付费软件包的一部分分发  

**商业许可证的优势：**
- ✨ 无需公开源代码
- ✨ 无 AGPL 约束
- ✨ 灵活集成到任何产品
- ✨ 完全的商业分发权
- ✨ 优先技术支持

**获取商业许可证：**

请联系开发者 **Pengkai Chen**：
- 📧 **邮箱**：Kevinlasnh@outlook.com  
- 📞 **电话**：+86 135-9049-3083  
- 💬 **GitHub**：在项目 issue 中标记 `commercial-license`

---

### 快速判断：你需要哪个许可证？

```
你的代码是否从这个项目中获利？
    ↓ YES → 需要商业许可证
    ↓ NO  → 继续看下面

你愿意开源整个项目吗（AGPL-3.0）？
    ↓ YES → 可以使用免费的 AGPL-3.0
    ↓ NO  → 需要商业许可证

还不确定？→ 联系 Kevinlasnh@outlook.com
```

---

### ⚠️ 重要警告

**不获取商业许可证进行商业使用将违反著作权法！** 可能导致：
- 立即中止许可
- 法律诉讼
- 赔偿损失和许可费
- 禁止令

详见项目 [LICENSE](LICENSE) 文件。
