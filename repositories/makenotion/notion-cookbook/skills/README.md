# Skills

AI-powered workflows that make it easier to work with Notion.

## What are skills?

Skills are structured instructions that help AI assistants perform complex tasks in Notion. They combine multiple API calls and decision-making logic into reusable workflows.

## Available skills

### Claude skills

The [claude](claude/) directory contains skills designed for use with Claude and the Notion MCP server:

- **[knowledge-capture](claude/knowledge-capture/)**: Transform conversations and discussions into structured documentation
- **[meeting-intelligence](claude/meeting-intelligence/)**: Prepare for meetings by gathering context and creating agendas
- **[research-documentation](claude/research-documentation/)**: Research topics and document findings in Notion
- **[spec-to-implementation](claude/spec-to-implementation/)**: Parse specifications and create implementation plans with task tracking

## Using skills

To use these skills with Claude:

1. Set up the [Notion MCP server](https://developers.notion.com/docs/notion-mcp) in your Claude configuration
2. Add the skill files to your Claude skills directory
3. The skills will activate automatically when you ask Claude to perform relevant tasks

See the [Claude skills README](claude/README.md) for detailed setup instructions.

## Contributing skills

Want to add a skill? Check out [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

Skills should:

- Solve a specific, common workflow
- Include evaluations that test effectiveness
- Be well documented with clear examples
- Follow best practices for the AI provider

## Future providers

As the ecosystem grows, we'll add skills for other AI tools and platforms. If you've built skills for another provider, we'd love to include them.
