# 贡献指南

感谢您对 WellAlly-health 项目的关注！我们欢迎任何形式的贡献。

## 📋 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [报告问题](#报告问题)
- [提交代码](#提交代码)
- [代码规范](#代码规范)
- [提交信息规范](#提交信息规范)

## 🤝 行为准则

参与此项目即表示您同意遵守我们的 [行为准则 (CODE_OF_CONDUCT.md)](CODE_OF_CONDUCT.md)：

- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

## 🚀 如何贡献

### 报告 Bug

这是帮助项目的一种非常有益的方式。如果您在使用过程中遇到问题：

1. 检查 [Issues](https://github.com/huifer/WellAlly-health/issues) 确保问题尚未被报告
2. 如果没有找到相关问题，创建一个新 Issue
3. 使用 Bug 报告模板，提供尽可能详细的信息
4. 包含复现步骤、预期行为和实际行为

### 提出新功能

如果您有新功能的想法：

1. 先在 [Issues](https://github.com/huifer/WellAlly-health/issues) 中讨论
2. 解释用例和为什么这个功能有用
3. 如果获得积极反馈，可以开始实现

### 🌟 新手友好任务（Good First Issues）

不知道从哪入手？我们为新手准备了友好任务：

- 🏷️ 浏览 [**good first issue**](https://github.com/huifer/WellAlly-health/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) 标签下的任务
- 💡 或查看 [**help wanted**](https://github.com/huifer/WellAlly-health/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
- 💬 在 [GitHub Discussions](https://github.com/huifer/WellAlly-health/discussions) 里提问或认领任务
- 📖 先读 [README](README.md) 与 [用户指南](docs/user-guide.md) 了解整体结构

常见的低门槛贡献：补充命令文档示例、翻译文档、新增药物相互作用规则、完善某个专科 Skill。

### 🖥️ 本地试用项目

在改动代码前，建议先本地试用 WellAlly Health，了解它如何工作：

```bash
# 前置：已安装 Claude Code
git clone https://github.com/huifer/WellAlly-health.git
cd WellAlly-health
# 在 Claude Code 中打开本目录，然后尝试：
/profile set 175 70 1990-01-01
/save-report /path/to/a-report.jpg
/query all
```

体验真实数据流，能帮你提出更贴合用户需求的改进。

### 提交代码

我们欢迎 Pull Request！以下是如何进行：

## 🔧 提交代码

### 开发流程

1. **Fork 项目**
   ```bash
   # 在 GitHub 上点击 Fork 按钮
   ```

2. **克隆您的 Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/WellAlly-health.git
   cd WellAlly-health
   ```

3. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或修复 bug
   git checkout -b fix/your-bug-fix
   ```

4. **进行更改**
   - 遵循项目的代码规范
   - 添加必要的测试
   - 更新相关文档

5. **提交更改**
   ```bash
   git add .
   git commit -m "type: description"
   ```

6. **推送到您的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 填写 PR 模板
   - 等待代码审查

### 分支命名

使用清晰的分支命名约定：

- `feature/` - 新功能
  ```bash
   feature/add-blood-pressure-tracking
  ```
- `fix/` - Bug 修复
  ```bash
  fix/fix-date-parsing-error
  ```
- `docs/` - 文档更新
  ```bash
  docs/update-readme-installation
  ```
- `refactor/` - 代码重构
  ```bash
  refactor/optimize-data-structure
  ```
- `test/` - 测试相关
  ```bash
  test/add-unit-tests-for-medication
  ```

## 📝 代码规范

### 文件组织

- 保持文件结构清晰和模块化
- 使用有意义的文件名和目录名
- 相关功能应该组织在一起

### 代码风格

- **一致性**: 保持与项目现有代码风格一致
- **注释**: 复杂逻辑必须添加注释说明
- **命名**: 使用清晰、描述性的变量和函数名
- **简洁**: 避免不必要的复杂性和冗余代码

### 文档

- 更新相关的 Markdown 文档
- 为新功能添加使用示例
- 保持中英文混合风格（符合项目现状）

## 💬 提交信息规范

我们使用语义化提交信息，格式如下：

```
<type>(<scope>): <subject>
```

### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行的变动）
- `refactor`: 重构（既不是新功能也不是修复）
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `ci`: CI 配置文件和脚本的变动

### Scope 范围

指定提交影响的范围，例如：

- `profile`: 用户档案
- `medication`: 用药管理
- `radiation`: 辐射管理
- `consult`: 会诊系统
- `docs`: 文档

### Subject 主题

描述变更的简短摘要：

- 使用祈使句，现在时态："change" 而不是 "changed" 或 "changes"
- 首字母小写
- 不要以句号结尾

### 示例

```bash
feat(medication): add drug interaction checking
fix(radiation): correct dose calculation for children
docs(readme): update installation instructions
refactor(data): optimize json structure for better performance
```

## 🧪 测试

- 为新功能添加测试
- 确保所有测试通过
- 手动测试关键功能

## 📧 联系方式

如有任何问题，请通过以下方式联系我们：

- 参与 [GitHub Discussions](https://github.com/huifer/WellAlly-health/discussions) 讨论
- 创建 [GitHub Issue](https://github.com/huifer/WellAlly-health/issues)
- 访问 [WellAlly Tech](https://www.wellally.tech/)

## ⚖️ 许可

通过贡献代码，您同意您的贡献将根据项目的 [MIT License](LICENSE) 进行许可。

---

再次感谢您的贡献！🎉
