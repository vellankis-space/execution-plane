# Docker MCP Toolkit

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

The Docker MCP Toolkit is a management interface integrated into Docker Desktop
that lets you set up, manage, and run containerized MCP servers and connect
them to AI agents. It removes friction from tool usage by offering secure
defaults, easy setup, and support for a growing ecosystem of LLM-based clients.
It is the fastest way from MCP tool discovery to local execution.

## Key features

- Cross-LLM compatibility: Works with Claude, Cursor, and other MCP clients.
- Integrated tool discovery: Browse and launch MCP servers from the Docker MCP Catalog directly in Docker Desktop.
- Zero manual setup: No dependency management, runtime configuration, or setup required.
- Functions as both an MCP server aggregator and a gateway for clients to access installed MCP servers.

> [!TIP]
> The MCP Toolkit includes [Dynamic MCP](/manuals/ai/mcp-catalog-and-toolkit/dynamic-mcp.md),
> which enables AI agents to discover, add, and compose MCP servers on-demand during
> conversations, without manual configuration. Your agent can search the catalog and
> add tools as needed when you connect to the gateway.

## How the MCP Toolkit works

MCP introduces two core concepts: MCP clients and MCP servers.

- MCP clients are typically embedded in LLM-based applications, such as the
  Claude Desktop app. They request resources or actions.
- MCP servers are launched by the client to perform the requested tasks, using
  any necessary tools, languages, or processes.

Docker standardizes the development, packaging, and distribution of
applications, including MCP servers. By packaging MCP servers as containers,
Docker eliminates issues related to isolation and environment differences. You
can run a container directly, without managing dependencies or configuring
runtimes.

Depending on the MCP server, the tools it provides might run within the same
container as the server or in dedicated containers for better isolation.

## Security

The Docker MCP Toolkit combines passive and active measures to reduce attack
surfaces and ensure safe runtime behavior.

### Passive security

Passive security refers to measures implemented at build-time, when the MCP
server code is packaged into a Docker image.

- Image signing and attestation: All MCP server images under `mcp/` in the [MCP
  Catalog](catalog.md) are built by Docker and digitally signed to verify their
  source and integrity. Each image includes a Software Bill of Materials (SBOM)
  for full transparency.

### Active security

Active security refers to security measures at runtime, before and after tools
are invoked, enforced through resource and access limitations.

- CPU allocation: MCP tools are run in their own container. They are
  restricted to 1 CPU, limiting the impact of potential misuse of computing
  resources.
- Memory allocation: Containers for MCP tools are limited to 2 GB.
- Filesystem access: By default, MCP Servers have no access to the host filesystem.
  The user explicitly selects the servers that will be granted file mounts.
- Interception of tool requests: Requests to and from tools that contain sensitive
  information such as secrets are blocked.

### OAuth authentication

Some MCP servers require authentication to access external services like
GitHub, Notion, and Linear. The MCP Toolkit handles OAuth authentication
automatically. You authorize access through your browser, and the Toolkit
manages credentials securely. You don't need to manually create API tokens or
configure authentication for each service.

#### Authorize a server with OAuth

<div
  class="tabs"

    x-data="{ selected: 'Docker-Desktop' }"

  aria-role="tabpanel"

<div aria-role="tablist" class="tablist">

    <button
        class="tab-item"
        :class="selected === 'Docker-Desktop' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'Docker-Desktop'"

    >
        Docker Desktop`</button>`

    <button
        class="tab-item"
        :class="selected === 'CLI' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'CLI'"

    >
        CLI`</button>`

</div>
  <div>


  

    `<div
        aria-role="tab"
        :class="selected !== 'Docker-Desktop' && 'hidden'"
      >`
        `<ol>`

<li>In Docker Desktop, go to <strong>MCP Toolkit</strong> and select the <strong>Catalog</strong> tab.</li>
<li>Find and add an MCP server that requires OAuth.</li>
<li>In the server's <strong>Configuration</strong> tab, select the <strong>OAuth</strong> authentication
method. Follow the link to begin the OAuth authorization.</li>
<li>Your browser opens the authorization page for the service. Follow the
on-screen instructions to complete authentication.</li>
<li>Return to Docker Desktop when authentication is complete.</li>
</ol>
<p>View all authorized services in the <strong>OAuth</strong> tab. To revoke access, select
<strong>Revoke</strong> next to the service you want to disconnect.</p>

    `</div>`

    `<div
        aria-role="tab"
        :class="selected !== 'CLI' && 'hidden'"
      >`
        `<p>`Enable an MCP server:`</p>`

<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'JCBkb2NrZXIgbWNwIHNlcnZlciBlbmFibGUgZ2l0aHViLW9mZmljaWFs', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-console" data-lang="console"><span class="line">``<span class="cl"><span class="gp">`$ docker mcp server `<span class="nb">`enable github-official
`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>If the server requires OAuth, authorize the connection:</p>
<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>



If the server requires OAuth, authorize the connection:


<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'JCBkb2NrZXIgbWNwIG9hdXRoIGF1dGhvcml6ZSBnaXRodWI=', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-console" data-lang="console"><span class="line">``<span class="cl"><span class="gp">`$ docker mcp oauth authorize github
`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>Your browser opens the authorization page. Complete the authentication process,
then return to your terminal.</p>
<p>View authorized services:</p>
<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>



Your browser opens the authorization page. Complete the authentication process,
then return to your terminal.


View authorized services:


<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'JCBkb2NrZXIgbWNwIG9hdXRoIGxz', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-console" data-lang="console"><span class="line">``<span class="cl"><span class="gp">`$ docker mcp oauth ls
`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>Revoke access to a service:</p>
<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>



Revoke access to a service:


<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'JCBkb2NrZXIgbWNwIG9hdXRoIHJldm9rZSBnaXRodWI=', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-console" data-lang="console"><span class="line">``<span class="cl"><span class="gp">`$ docker mcp oauth revoke github
`</code></pre>``</div>`

    `</div>`

</div>
</div>


    `</div>`

</div>
</div>


## Usage examples

### Example: Use the GitHub Official MCP server with Ask Gordon

To illustrate how the MCP Toolkit works, here's how to enable the GitHub
Official MCP server and use [Ask Gordon](/manuals/ai/gordon/_index.md) to
interact with your GitHub account:

1. From the **MCP Toolkit** menu in Docker Desktop, select the **Catalog** tab
   and find the **GitHub Official** server and add it.
2. In the server's **Configuration** tab, authenticate via OAuth.
3. In the **Clients** tab, ensure Gordon is connected.
4. From the **Ask Gordon** menu, you can now send requests related to your
   GitHub account, in accordance to the tools provided by the GitHub Official
   server. To test it, ask Gordon:

   ```text
   What's my GitHub handle?
   ```

   Make sure to allow Gordon to interact with GitHub by selecting **Always
   allow** in Gordon's answer.

> [!TIP]
> The Gordon client is enabled by default,
> which means Gordon can automatically interact with your MCP servers.

### Example: Use Claude Desktop as a client

Imagine you have Claude Desktop installed, and you want to use the GitHub MCP server,
and the Puppeteer MCP server, you do not have to install the servers in Claude Desktop.
You can simply install these 2 MCP servers in the MCP Toolkit,
and add Claude Desktop as a client:

1. From the **MCP Toolkit** menu, select the **Catalog** tab and find the **Puppeteer** server and add it.
2. Repeat for the **GitHub Official** server.
3. From the **Clients** tab, select **Connect** next to **Claude Desktop**. Restart
   Claude Desktop if it's running, and it can now access all the servers in the MCP Toolkit.
4. Within Claude Desktop, run a test by submitting the following prompt using the Sonnet 3.5 model:

   ```text
   Take a screenshot of docs.docker.com and then invert the colors
   ```

### Example: Use Visual Studio Code as a client

You can interact with all your installed MCP servers in Visual Studio Code:

1. To enable the MCP Toolkit:

<div
  class="tabs"

    x-data="{ selected: 'Enable-globally' }"

  aria-role="tabpanel"

<div aria-role="tablist" class="tablist">

    <button
        class="tab-item"
        :class="selected === 'Enable-globally' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'Enable-globally'"

    >
        Enable globally`</button>`

    <button
        class="tab-item"
        :class="selected === 'Enable-for-a-given-project' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'Enable-for-a-given-project'"

    >
        Enable for a given project`</button>`

</div>
  <div>


  
    `<div
        aria-role="tab"
        :class="selected !== 'Enable-globally' && 'hidden'"
      >`
        `<ol>`

<li>
<p>Insert the following in your Visual Studio Code's User <code>mcp.json</code>:</p>
<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'Im1jcCI6IHsKICJzZXJ2ZXJzIjogewogICAiTUNQX0RPQ0tFUiI6IHsKICAgICAiY29tbWFuZCI6ICJkb2NrZXIiLAogICAgICJhcmdzIjogWwogICAgICAgIm1jcCIsCiAgICAgICAiZ2F0ZXdheSIsCiAgICAgICAicnVuIgogICAgIF0sCiAgICAgInR5cGUiOiAic3RkaW8iCiAgIH0KIH0KfQ==', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-json" data-lang="json"><span class="line">``<span class="cl"><span class="s2">`&#34;mcp&#34;`<span class="err">`: `<span class="p">`{
`<span class="line"><span class="cl">` `<span class="nt">`&#34;servers&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`   `<span class="nt">`&#34;MCP_DOCKER&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`     `<span class="nt">`&#34;command&#34;`<span class="p">`: `<span class="s2">`&#34;docker&#34;`<span class="p">`,
`<span class="line"><span class="cl">`     `<span class="nt">`&#34;args&#34;`<span class="p">`: `<span class="p">`[
`<span class="line"><span class="cl">`       `<span class="s2">`&#34;mcp&#34;`<span class="p">`,
`<span class="line"><span class="cl">`       `<span class="s2">`&#34;gateway&#34;`<span class="p">`,
`<span class="line"><span class="cl">`       `<span class="s2">`&#34;run&#34;
`<span class="line"><span class="cl">`     `<span class="p">`],
`<span class="line"><span class="cl">`     `<span class="nt">`&#34;type&#34;`<span class="p">`: `<span class="s2">`&#34;stdio&#34;
`<span class="line"><span class="cl">`   `<span class="p">`}
`<span class="line"><span class="cl">` `<span class="p">`}
`<span class="line"><span class="cl">``<span class="p">`}`</code></pre>``</div>`

    `</div>`

</div>
</div>
</li>
</ol>




    `</div>`

    `<div
        aria-role="tab"
        :class="selected !== 'Enable-for-a-given-project' && 'hidden'"
      >`
        `<ol>`

<li>
<p>In your terminal, navigate to your project's folder.</p>
</li>
<li>
<p>Run:</p>
<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'ZG9ja2VyIG1jcCBjbGllbnQgY29ubmVjdCB2c2NvZGU=', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-bash" data-lang="bash"><span class="line">``<span class="cl">`docker mcp client connect vscode`</code></pre>``</div>`

    `</div>`

</div>
</div>


<blockquote

    class="admonition admonition-note admonition not-prose">`<div class="admonition-header">`
      `<span class="admonition-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">`
`<path d="M12 16V12M12 8H12.01M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`
`</svg>`

    `<span class="admonition-title">`
        Note
    
    `</div>`
    `<div class="admonition-content">`
      `<p>`This command creates a `<code>`.vscode/mcp.json`</code>` file in the current
directory. As this is a user-specific file, add it to your `<code>`.gitignore`</code>`
file to prevent it from being committed to the repository.`</p>`

<div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"
>

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'ZWNobyAiLnZzY29kZS9tY3AuanNvbiIgPj4gLmdpdGlnbm9yZQ==', copying: false }"
        class="
          top-1
         absolute right-2 z-10 text-gray-300 dark:text-gray-500"
        title="copy"
        @click="window.navigator.clipboard.writeText(atob(code).replaceAll(/^[\$>]\s+/gm, ''));
      copying = true;
      setTimeout(() => copying = false, 2000);"
      >
        `<span
          :class="{ 'group-hover:block' : !copying }"
          class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="M300-200q-24 0-42-18t-18-42v-560q0-24 18-42t42-18h440q24 0 42 18t18 42v560q0 24-18 42t-42 18H300ZM180-80q-24 0-42-18t-18-42v-590q0-13 8.5-21.5T150-760q13 0 21.5 8.5T180-730v590h470q13 0 21.5 8.5T680-110q0 13-8.5 21.5T650-80H180Z"/></svg>``</span
        >`
        `<span :class="{ 'group-hover:block' : copying }" class="icon-svg hidden"
          ><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 -960 960 960">``<path d="m421-389-98-98q-9-9-22-9t-23 10q-9 9-9 22t9 22l122 123q9 9 21 9t21-9l239-239q10-10 10-23t-10-23q-10-9-23.5-8.5T635-603L421-389Zm59 309q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>``</span
        >`
      `</button>`

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-console" data-lang="console"><span class="line">``<span class="cl"><span class="go">`echo &#34;.vscode/mcp.json&#34; &gt;&gt; .gitignore
`</code></pre>``</div>`

    `</div>`

</div>
</div>
    </div>
  </blockquote>



  
  
</li>
</ol>

    `</div>`

</div>
</div>


1. In Visual Studio Code, open a new Chat and select the **Agent** mode:

   ![Copilot mode switching](./images/copilot-mode.png)
2. You can also check the available MCP tools:

   ![Displaying tools in VSCode](./images/tools.png)

For more information about the Agent mode, see the
[Visual Studio Code documentation](https://code.visualstudio.com/docs/copilot/chat/mcp-servers#_use-mcp-tools-in-agent-mode).

## Further reading

- [MCP Catalog](/manuals/ai/mcp-catalog-and-toolkit/catalog.md)
- [MCP Gateway](/manuals/ai/mcp-catalog-and-toolkit/mcp-gateway.md)
