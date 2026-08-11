# Prisma Cursor Plugin

A comprehensive Cursor plugin for Prisma development, providing MCP server integration, AI rules, specialized skills, custom agents, and automation hooks.

## Features

### 🔌 MCP Server Integration
- Direct integration with Prisma MCP server
- Database introspection and querying
- Schema management through AI

### 📋 Rules
- **Schema Conventions**: Enforces Prisma naming conventions and best practices
- **Migration Best Practices**: Guidelines for safe database migrations

### 🎯 Skills
- **Schema Designer**: Design and modify Prisma schemas following best practices
- **Migration Manager**: Safely create, deploy, and manage database migrations

### 🤖 Custom Agents
- **Prisma Expert**: Comprehensive Prisma development expertise
- **Schema Reviewer**: Specialized schema review and optimization

### ⚡ Automation Hooks
- **Pre-commit**: Validates Prisma schema before commits
- **Post-save**: Auto-formats Prisma schema files on save
- **On-schema-change**: Regenerates TypeScript types after schema changes

## Installation

### From Cursor Marketplace
```bash
# Install via Cursor CLI
cursor plugin install prisma-cursor-plugin
```

### Manual Installation
1. Clone this repository
2. Copy to your Cursor plugins directory
3. Run setup script:
```bash
npm run setup
```

## Configuration

### Database Connection

Create a `.env` file in your project root:

```env
DATABASE_URL="postgresql://user:password@localhost:5432/mydb"
```

### MCP Server

The Prisma MCP server is automatically configured. Ensure your `DATABASE_URL` environment variable is set.

## Usage

### Using Rules

Rules are automatically applied to your Prisma schema files:
- Schema conventions enforce naming standards
- Migration best practices guide safe database changes

### Using Skills

Invoke skills via Cursor AI:
- `/schema-designer` - Design new schemas or modify existing ones
- `/migration-manager` - Create and manage migrations

### Using Agents

Switch to custom agents in Cursor:
- **Prisma Expert**: For general Prisma development tasks
- **Schema Reviewer**: For schema reviews and optimization

### Automation Hooks

Hooks run automatically on configured events:
- Schema validation before commits
- Auto-formatting on save
- Type generation after schema changes

## Project Structure

```
prisma-cursor-plugin/
├── .cursor/
│   └── plugin.json           # Plugin manifest
├── rules/
│   ├── schema-conventions.mdc
│   └── migration-best-practices.mdc
├── skills/
│   ├── schema-designer/
│   │   └── SKILL.md
│   └── migration-manager/
│       └── SKILL.md
├── agents/
│   ├── prisma-expert.md
│   └── schema-reviewer.md
├── scripts/
│   ├── setup.sh
│   ├── pre-commit.sh
│   ├── format-schema.js
│   └── generate-types.ts
├── hooks.json                # Hook definitions
├── mcp.json                  # MCP server configuration
├── package.json
└── README.md
```

## Development

### Scripts

```bash
# Setup the plugin
npm run setup

# Build MCP server (when implemented)
npm run build

# Development mode (when implemented)
npm run dev

# Run code generation scripts
npm run generate
```

## Requirements

- Node.js >= 18
- Prisma CLI (installed automatically by setup)
- Database connection (PostgreSQL, MySQL, SQLite, etc.)

## Examples

### Creating a Schema

```prisma
model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([email])
}

model Post {
  id          Int      @id @default(autoincrement())
  title       String
  content     String?
  published   Boolean  @default(false)
  authorId    Int
  author      User     @relation(fields: [authorId], references: [id])
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  @@index([authorId])
  @@index([published])
}
```

### Creating a Migration

```bash
# Create and apply migration
npx prisma migrate dev --name add_user_posts

# Deploy to production
npx prisma migrate deploy
```

## Contributing

Contributions are welcome! Please follow Prisma's contribution guidelines.

## License

MIT

## Support

- [Prisma Documentation](https://www.prisma.io/docs)
- [Prisma Community](https://www.prisma.io/community)
- [GitHub Issues](https://github.com/prisma/cursor-plugin/issues)
