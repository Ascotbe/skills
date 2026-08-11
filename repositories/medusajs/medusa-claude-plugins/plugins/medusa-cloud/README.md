# Medusa Cloud Plugin

Skills for managing Medusa Cloud resources through the Cloud CLI (`mcloud`). Covers setup, deployments, debugging, local build reproduction, environment management, and variables.

> For installation and usage with other agents, refer to the [main README](../../README.md).

## Installation with Claude Code

### Prerequisites

- [Claude Code](https://github.com/anthropics/claude-code) installed
- A Medusa Cloud account (or planning to create one)

### Install Plugin

1. Start Claude:

```bash
claude
```

2. Add Medusa marketplace to Claude Code:

```bash
/plugin marketplace add medusajs/medusa-agent-skills
```

3. Install the plugin:

```bash
/plugin install medusa-cloud@medusa
```

4. Verify the plugin is loaded:

```bash
/plugin
```

## Skills Included

1. **using-medusa-cloud** - Workflow guide for Cloud CLI operations (setup, deployments, debugging, environments, variables)
2. **mcloud-auth** - Execute `mcloud whoami`, `mcloud use`, `mcloud login`, `mcloud logout`, `mcloud version`
3. **mcloud-deployments** - Execute `mcloud deployments list/get/build-logs`
4. **mcloud-environments** - Execute `mcloud environments list/get/create/delete/redeploy/trigger-build`
5. **mcloud-logs** - Execute `mcloud logs` with all filter options
6. **mcloud-variables** - Execute `mcloud variables list/get/set/delete`
7. **mcloud-organizations** - Execute `mcloud organizations list/get`
8. **mcloud-projects** - Execute `mcloud projects list/get/delete`
9. **mcloud-local** - Execute `mcloud local build` to reproduce a Cloud build locally

## Privacy

This plugin does not collect, store, or transmit any user data or conversation information. All instructional content is provided locally through skill files.
