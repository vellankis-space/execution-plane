# Docker MCP Catalog

<div
    class="not-prose summary-bar"
  >

    `<div class="flex flex-wrap gap-1">`
        `<span class="font-bold">`Availability:
        `<span>`
          Beta

    `<span class="icon-svg"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M360-360H217q-18 0-26.5-16t2.5-31l338-488q8-11 20-15t24 1q12 5 19 16t5 24l-39 309h176q19 0 27 17t-4 32L388-66q-8 10-20.5 13T344-55q-11-5-17.5-16T322-95l38-265Z"/></svg>`

    `</div>`

</div>

The [Docker MCP Catalog](https://hub.docker.com/mcp) is a centralized, trusted
registry for discovering, sharing, and running MCP-compatible tools. Integrated
with Docker Hub, it offers verified, versioned, and curated MCP servers
packaged as Docker images. The catalog is also available in Docker Desktop.

The catalog solves common MCP server challenges:

- Environment conflicts. Tools often need specific runtimes that might clash
  with existing setups.
- Lack of isolation. Traditional setups risk exposing the host system.
- Setup complexity. Manual installation and configuration slow adoption.
- Inconsistency across platforms. Tools might behave unpredictably on different
  operating systems.

With Docker, each MCP server runs as a self-contained container. This makes it
portable, isolated, and consistent. You can launch tools instantly using the
Docker CLI or Docker Desktop, without worrying about dependencies or
compatibility.

## Key features

- Extensive collection of verified MCP servers in one place.
- Publisher verification and versioned releases.
- Pull-based distribution using Docker infrastructure.
- Tools provided by partners such as New Relic, Stripe, Grafana, and more.

> [!NOTE]
> E2B sandboxes now include direct access to the Docker MCP Catalog, giving developers
> access to over 200 tools and services to seamlessly build and run AI agents. For
> more information, see [E2B Sandboxes](sandboxes.md).

## How it works

Each tool in the MCP Catalog is packaged as a Docker image with metadata.

- Discover tools on Docker Hub under the `mcp/` namespace.
- Connect tools to your preferred agents with simple configuration through the
  [MCP Toolkit](toolkit.md).
- Pull and run tools using Docker Desktop or the CLI.

Each catalog entry displays:

- Tool description and metadata.
- Version history.
- List of tools provided by the MCP server.
- Example configuration for agent integration.

## Server deployment types

The Docker MCP Catalog supports both local and remote server deployments, each optimized for different use cases and requirements.

### Local MCP servers

Local MCP servers are containerized applications that run directly on your machine. All local servers are built and digitally signed by Docker, providing enhanced security through verified provenance and integrity. These servers run as containers on your local environment and function without internet connectivity once downloaded. Local servers display a Docker icon

<img
  loading="lazy"
  src="../../../desktop/images/whale-x.svg"
  alt="docker whale icon"

  class="inline my-0 not-prose"
/>
 to indicate they are built by Docker.

Local servers offer predictable performance, complete data privacy, and independence from external service availability. They work well for development workflows, sensitive data processing, and scenarios requiring offline functionality.

### Remote MCP servers

Remote MCP servers are hosted services that run on the provider's
infrastructure and connect to external services like GitHub, Notion, and
Linear. Many remote servers use OAuth authentication. When a remote server
requires OAuth, the MCP Toolkit handles authentication automatically - you
authorize access through your browser, and the Toolkit manages credentials
securely. You don't need to manually create API tokens or configure
authentication.

Remote servers display a cloud icon in the catalog. For setup instructions, see
[MCP Toolkit](toolkit.md#oauth-authentication).

## Use an MCP server from the catalog

To use an MCP server from the catalog, see [MCP Toolkit](toolkit.md).

## Contribute an MCP server to the catalog

The MCP server registry is available at
https://github.com/docker/mcp-registry. To submit an MCP server, follow the
[contributing guidelines](https://github.com/docker/mcp-registry/blob/main/CONTRIBUTING.md).

When your pull request is reviewed and approved, your MCP server is available
within 24 hours on:

- Docker Desktop's [MCP Toolkit feature](toolkit.md).
- The [Docker MCP Catalog](https://hub.docker.com/mcp).
- The [Docker Hub](https://hub.docker.com/u/mcp) `mcp` namespace (for MCP
  servers built by Docker).
