# GitHub网络连接问题解决方案

## 问题描述

您遇到的错误信息：
```
fatal: unable to access 'https://github.com/2668685889/video-analyzer.git/': Failed to connect to github.com port 443 after 75003 ms: Couldn't connect to server
```

这表示无法连接到GitHub服务器，通常是网络连接问题。

## 解决方案

### 方案一：检查网络连接

1. **测试网络连接**：
   ```bash
   ping github.com
   ```

2. **测试HTTPS连接**：
   ```bash
   curl -I https://github.com
   ```

### 方案二：使用代理（如果您在使用VPN或代理）

1. **配置Git代理**（如果您使用HTTP代理）：
   ```bash
   git config --global http.proxy http://proxy.server:port
   git config --global https.proxy https://proxy.server:port
   ```

2. **配置Git代理**（如果您使用SOCKS5代理）：
   ```bash
   git config --global http.proxy socks5://127.0.0.1:1080
   git config --global https.proxy socks5://127.0.0.1:1080
   ```

3. **取消代理配置**（如果不需要代理）：
   ```bash
   git config --global --unset http.proxy
   git config --global --unset https.proxy
   ```

### 方案三：使用SSH方式推送（推荐）

1. **生成SSH密钥**（如果还没有）：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **添加SSH密钥到ssh-agent**：
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. **复制公钥内容**：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

4. **在GitHub上添加SSH密钥**：
   - 登录GitHub
   - 进入Settings → SSH and GPG keys
   - 点击"New SSH key"
   - 粘贴公钥内容

5. **更改远程仓库URL为SSH格式**：
   ```bash
   git remote set-url origin git@github.com:2668685889/video-analyzer.git
   ```

6. **测试SSH连接**：
   ```bash
   ssh -T git@github.com
   ```

7. **推送代码**：
   ```bash
   git push -u origin main
   ```

### 方案四：使用GitHub CLI（最简单）

由于我们已经安装了GitHub CLI，可以使用它来推送：

1. **重新进行身份验证**：
   ```bash
   gh auth login
   ```
   选择：
   - GitHub.com
   - HTTPS
   - Yes（authenticate Git with your GitHub credentials）
   - Login with a web browser

2. **推送代码**：
   ```bash
   git push -u origin main
   ```

### 方案五：检查防火墙和DNS

1. **检查DNS解析**：
   ```bash
   nslookup github.com
   ```

2. **尝试使用不同的DNS**：
   ```bash
   # 临时使用Google DNS
   sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4
   ```

3. **重置DNS（恢复默认）**：
   ```bash
   sudo networksetup -setdnsservers Wi-Fi "Empty"
   ```

## 推荐解决流程

1. **首先尝试方案四**（GitHub CLI）- 最简单
2. **如果不行，尝试方案三**（SSH）- 最稳定
3. **如果还是不行，检查方案一和方案五**（网络问题）

## 成功推送后的验证

推送成功后，您可以：

1. **访问GitHub仓库**：
   https://github.com/2668685889/video-analyzer

2. **查看GitHub Actions**：
   - 进入仓库的"Actions"标签页
   - 查看自动编译进度

3. **下载编译结果**：
   - 编译完成后，在"Actions"页面下载Windows可执行文件

## 常见问题

**Q: 为什么会出现连接超时？**
A: 通常是网络问题、防火墙阻止或DNS解析问题。

**Q: 使用代理时应该注意什么？**
A: 确保代理服务器地址和端口正确，并且代理服务正在运行。

**Q: SSH方式和HTTPS方式有什么区别？**
A: SSH方式更安全稳定，不需要每次输入密码；HTTPS方式更简单，但可能遇到网络问题。

---

**提示**：如果您在公司网络环境中，可能需要联系网络管理员获取代理配置信息。