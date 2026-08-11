# Contributing Guidelines

Thank you for your interest in the WellAlly-health project! We welcome contributions in any form.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Issues](#reporting-issues)
- [Submitting Code](#submitting-code)
- [Coding Standards](#coding-standards)
- [Commit Message Convention](#commit-message-convention)

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct (CODE_OF_CONDUCT.md)](CODE_OF_CONDUCT.md):

- Respect differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 How to Contribute

### Reporting Bugs

This is a very helpful way to contribute to the project. If you encounter issues during use:

1. Check [Issues](https://github.com/huifer/WellAlly-health/issues) to ensure the problem hasn't been reported
2. If you don't find a related issue, create a new one
3. Use the bug report template and provide as much detail as possible
4. Include reproduction steps, expected behavior, and actual behavior

### Suggesting New Features

If you have ideas for new features:

1. Discuss in [Issues](https://github.com/huifer/WellAlly-health/issues) first
2. Explain the use case and why this feature would be useful
3. If you receive positive feedback, you can start implementing

### 🌟 Good First Issues

Not sure where to start? We curate beginner-friendly tasks:

- 🏷️ Browse the [**good first issue**](https://github.com/huifer/WellAlly-health/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label
- 💡 Or see [**help wanted**](https://github.com/huifer/WellAlly-health/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22)
- 💬 Ask or claim a task in [GitHub Discussions](https://github.com/huifer/WellAlly-health/discussions)
- 📖 Read the [README](README.md) and [User Guide](docs/user-guide.en.md) first

Common low-threshold contributions: command doc examples, translations, new
drug-interaction rules, or improving a specialty Skill.

### 🖥️ Try It Locally First

Before changing code, try WellAlly Health locally to understand how it works:

```bash
# Prerequisite: Claude Code installed
git clone https://github.com/huifer/WellAlly-health.git
cd WellAlly-health
# Open this directory in Claude Code, then try:
/profile set 175 70 1990-01-01
/save-report /path/to/a-report.jpg
/query all
```

Experiencing the real data flow helps you propose user-centered improvements.

### Submitting Code

We welcome Pull Requests! Here's how to get started:

## 🔧 Submitting Code

### Development Workflow

1. **Fork the Project**
   ```bash
   # Click the Fork button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/WellAlly-health.git
   cd WellAlly-health
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # Or fix a bug
   git checkout -b fix/your-bug-fix
   ```

4. **Make Changes**
   - Follow the project's coding standards
   - Add necessary tests
   - Update relevant documentation

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "type: description"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Create a Pull Request on GitHub
   - Fill out the PR template
   - Wait for code review

### Branch Naming

Use clear branch naming conventions:

- `feature/` - New features
  ```bash
  feature/add-blood-pressure-tracking
  ```
- `fix/` - Bug fixes
  ```bash
  fix/fix-date-parsing-error
  ```
- `docs/` - Documentation updates
  ```bash
  docs/update-readme-installation
  ```
- `refactor/` - Code refactoring
  ```bash
  refactor/optimize-data-structure
  ```
- `test/` - Test related
  ```bash
  test/add-unit-tests-for-medication
  ```

## 📝 Coding Standards

### File Organization

- Keep file structure clear and modular
- Use meaningful file and directory names
- Related functionality should be organized together

### Code Style

- **Consistency**: Maintain consistency with the existing project code style
- **Comments**: Add comments for complex logic
- **Naming**: Use clear, descriptive variable and function names
- **Simplicity**: Avoid unnecessary complexity and redundant code

### Documentation

- Update relevant Markdown documentation
- Add usage examples for new features
- Maintain bilingual style (Chinese and English) to match project standards

## 💬 Commit Message Convention

We use semantic commit messages with the following format:

```
<type>(<scope>): <subject>
```

### Type Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code formatting (changes that don't affect code execution)
- `refactor`: Refactoring (neither new feature nor fix)
- `perf`: Performance optimization
- `test`: Testing related
- `chore`: Changes to build process or auxiliary tools
- `ci`: CI configuration files and script changes

### Scope

Specify the scope of the commit's impact, for example:

- `profile`: User profile
- `medication`: Medication management
- `radiation`: Radiation management
- `consult`: Consultation system
- `docs`: Documentation

### Subject

A brief summary describing the change:

- Use imperative mood, present tense: "change" not "changed" nor "changes"
- First letter lowercase
- Don't end with a period

### Examples

```bash
feat(medication): add drug interaction checking
fix(radiation): correct dose calculation for children
docs(readme): update installation instructions
refactor(data): optimize json structure for better performance
```

## 🧪 Testing

- Add tests for new features
- Ensure all tests pass
- Manually test critical functionality

## 📧 Contact

If you have any questions, please contact us through:

- Join [GitHub Discussions](https://github.com/huifer/WellAlly-health/discussions)
- Create a [GitHub Issue](https://github.com/huifer/WellAlly-health/issues)
- Visit [WellAlly Tech](https://www.wellally.tech/)

## ⚖️ License

By contributing code, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

---

Thank you again for your contribution! 🎉
