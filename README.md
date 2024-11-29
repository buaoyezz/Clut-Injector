# **Clut-Injector**
### 目录

- [功能](#功能)
- [安装](#安装)
- [使用方法](#使用方法)
- [注意事项](#注意事项)
- [关于进步](#关于进步)
- [未来计划](#未来计划)
- [基础构建环境搭建](#基础构建环境搭建)

`Clut-Injector` 是一个用于在 Windows 平台上进行注入操作的工具。它可以帮助用户将 DLL 注入到目标进程中，以便执行各种任务或修改进程行为

`Clut-Injector*` 请注意所有注入器都会爆毒，被安全软件制裁，但是本软件一定无后门!若是你不相信我，你可以自己检查源码然后编译，不要传谣我放了BackDoor.

## 功能

- **DLL 注入**：将 DLL 文件注入到指定的进程中
- **用户友好的界面**：提供简单的图形用户界面（GUI）以进行注入操作。
- **日志记录**：记录注入操作的详细日志，以帮助诊断和调试。

## 安装

1. **下载**：从 [发布页面](https://github.com/buaoyezz/Clut-Injector/releases/)下载最新的可执行文件
   
2. **解压**：将下载的文件解压到你希望安装的位置

3. **运行**：双击 `Clut-Injector.exe` 启动程序。如果你在 Windows 上遇到权限问题，尝试以管理员权限运行程序

## 使用方法

1. **启动程序**：
   - 双击 `Clut-Injector.exe` 启动程序
   
2. **选择 DLL 文件**：
   - 在程序界面中，点击“选择 DLL”按钮，浏览并选择你希望注入的 DLL 文件
   - 支持多dll同时注入

3. **选择目标进程**：
   - 从进程列表中选择你希望将 DLL 注入到的目标进程

4. **执行注入**：
   - 点击“注入”按钮开始注入操作。程序将尝试将 DLL 注入到所选进程中

5. **查看日志**：
   - 日志相伴，注入问题一眼明了

6. **关于附加**：
   - 本软件的icons是附加包，所以可选择不附加(即删除也不会影响软件正常运行)
   - 从2.0.0版本开始，本软件内置dll，不再需要dll文件单独放置
   - 本软件2.0.0版本开始支持便携版，便携版不会自带图标，即开即用
   - 本软件2.0.0版本开始支持自动构建，只要保证有pyinstaller的基础即可


## 注意事项

- **管理员权限**：某些操作可能需要管理员权限。请确保以管理员权限运行程序，注入更加流畅
- **兼容性**：`Clut-Injector` 主要在 Windows 平台上运行，目前不支持其他操作系统
- **安全性**：请确保注入的 DLL 文件来自可信来源，避免潜在的安全风险 | 其次[`所有单纯的注入器都会被安全软件检测，建议拉入可信名单`，`若你不相信本程序，自己看源码并且构建即可`]
- **关于构建**: 本程序采用的是Pyinstaller+Cl的配合，通过Pyinstaller打包并且包含dll，同时软件内调用dll，进行注入，dll使用VS的cl工具构建｀详细看下面｀

## 关于进步

如果你想为 `Clut-Injector` 贡献代码或报告问题，请访问 [GitHub 仓库](https://github.com/buaoyezz/Clut-Injector/) 并提交问题或拉取请求

## 未来计划
 - 做更多的优化
 - 做更好的体验

## 基础构建环境搭建
> 克隆仓库
```bash
git clone https://github.com/buaoyezz/Clut--Injector.git
```
> Tips:项目主软件基于Python 3.13.0 开发完成
>> 安装Python[Python官网](https://python.org/)
>>> 开始前请`pip install -r requirements.txt`这很重要<br>
> 安装 PyInstaller（如果尚未安装）
```bash
pip install pyinstaller
```
> 使用 PyInstaller 打包 Python 程序
> 目前已经支持脚本自动编译了，只要保证有pyinstaller的基础就行
```bash
python build_script.py
```
+ DLL 编译:
> 1.打开 Microsoft Visual Studio 的开发者命令提示符
```bash
cl /LD path/to/ClutInject_Kernel.cpp /link /OUT:ClutInject_Kernel.dll
```
> 2.命令行编译方法(使用MSVC)：
```bash
:: 设置环境
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
:: 编译
cl /LD /MD ClutInject_Kernel.cpp /link /OUT:ClutInject_Kernel.dll
```
> 最后-> 你需要将dll放在软件下面在DOS窗口内即可看见内核是否已经载入成功
> 编译教程至此结束

> 项目开发不易，感谢使用支持!
>> Powered By ZZBuAoYe
## The End.
+ 感谢使用Clut-Injector
+ 持续更新ing......
