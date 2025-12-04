# Docker Hub MCP server

The Docker Hub MCP Server is a Model Context Protocol (MCP) server that
interfaces with Docker Hub APIs to make rich image metadata accessible to LLMs,
enabling intelligent content discovery and repository management.

For more information about MCP concepts and how MCP servers work, see the [Docker MCP Catalog and Toolkit](index.md) overview page.

## Key features

- Advanced LLM context: Docker's MCP Server provides LLMs with detailed, structured context for Docker Hub images, enabling smarter, more relevant recommendations for developers, whether they're choosing a base image or automating CI/CD workflows.
- Natural language image discovery: Developers can find the right container image using natural language, no need to remember tags or repository names. Just describe what you need, and Docker Hub will return images that match your intent.
- Simplified repository management: Hub MCP Server enables agents to manage repositories through natural language fetching image details, viewing stats, searching content, and performing key operations quickly and easily.

## Install Docker Hub MCP server

1. From the **MCP Toolkit** menu, select the **Catalog** tab and search for **Docker Hub** and select the plus icon to add the Docker Hub MCP server.
2. In the server's **Configuration** tab, insert your Docker Hub username and personal access token (PAT).
3. In the **Clients** tab in MCP Toolkit, ensure Gordon is connected.
4. From the **Ask Gordon** menu, you can now send requests related to your
   Docker Hub account, in accordance to the tools provided by the Docker Hub MCP server. To test it, ask Gordon:

   ```text
   What repositories are in my namespace?
   ```

> [!TIP]
> By default, the Gordon [client](/manuals/ai/mcp-catalog-and-toolkit/toolkit.md#install-an-mcp-client) is enabled,
> which means Gordon can automatically interact with your MCP servers.

## Use Claude Desktop as a client

1. Add the Docker Hub MCP Server configuration to your `claude_desktop_config.json`:

<div
  class="tabs"

    x-data="{ selected: 'For-public-repositories-only' }"

  aria-role="tabpanel"

<div aria-role="tablist" class="tablist">

    <button
        class="tab-item"
        :class="selected === 'For-public-repositories-only' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'For-public-repositories-only'"

    >
        For public repositories only`</button>`

    <button
        class="tab-item"
        :class="selected === 'For-authenticated-access' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'For-authenticated-access'"

    >
        For authenticated access`</button>`

</div>
  <div>


  

    `<div
        aria-role="tab"
        :class="selected !== 'For-public-repositories-only' && 'hidden'"
      >`
        <div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'ewogICJtY3BTZXJ2ZXJzIjogewogICAgImRvY2tlci1odWIiOiB7CiAgICAgICJjb21tYW5kIjogIm5vZGUiLAogICAgICAiYXJncyI6IFsiL0ZVTEwvUEFUSC9UTy9ZT1VSL2RvY2tlci1odWItbWNwLXNlcnZlci9kaXN0L2luZGV4LmpzIiwgIi0tdHJhbnNwb3J0PXN0ZGlvIl0KICAgIH0KICB9Cn0=', copying: false }"
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

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-json" data-lang="json"><span class="line">``<span class="cl"><span class="p">`{
`<span class="line"><span class="cl">`  `<span class="nt">`&#34;mcpServers&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`    `<span class="nt">`&#34;docker-hub&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;command&#34;`<span class="p">`: `<span class="s2">`&#34;node&#34;`<span class="p">`,
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;args&#34;`<span class="p">`: `<span class="p">`[`<span class="s2">`&#34;/FULL/PATH/TO/YOUR/docker-hub-mcp-server/dist/index.js&#34;`<span class="p">`, `<span class="s2">`&#34;--transport=stdio&#34;`<span class="p">`]
`<span class="line"><span class="cl">`    `<span class="p">`}
`<span class="line"><span class="cl">`  `<span class="p">`}
`<span class="line"><span class="cl">``<span class="p">`}`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>Where :</p>
<ul>
<li><code>/FULL/PATH/TO/YOUR/docker-hub-mcp-server</code> is the complete path to where you cloned the repository</li>
</ul>



Where :


* `/FULL/PATH/TO/YOUR/docker-hub-mcp-server` is the complete path to where you cloned the repository

    `</div>`

    `<div
        aria-role="tab"
        :class="selected !== 'For-authenticated-access' && 'hidden'"
      >`
        <div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'ewogICJtY3BTZXJ2ZXJzIjogewogICAgImRvY2tlci1odWIiOiB7CiAgICAgICJjb21tYW5kIjogIm5vZGUiLAogICAgICAiYXJncyI6IFsiL0ZVTEwvUEFUSC9UTy9ZT1VSL2RvY2tlci1odWItbWNwLXNlcnZlci9kaXN0L2luZGV4LmpzIiwgIi0tdHJhbnNwb3J0PXN0ZGlvIiwgIi0tdXNlcm5hbWU9WU9VUl9ET0NLRVJfSFVCX1VTRVJOQU1FIl0sCiAgICAgICJlbnYiOiB7CiAgICAgICAgIkhVQl9QQVRfVE9LRU4iOiAiWU9VUl9ET0NLRVJfSFVCX1BFUlNPTkFMX0FDQ0VTU19UT0tFTiIKICAgICAgfQogICAgfQogIH0KfQ==', copying: false }"
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

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-json" data-lang="json"><span class="line">``<span class="cl"><span class="p">`{
`<span class="line"><span class="cl">`  `<span class="nt">`&#34;mcpServers&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`    `<span class="nt">`&#34;docker-hub&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;command&#34;`<span class="p">`: `<span class="s2">`&#34;node&#34;`<span class="p">`,
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;args&#34;`<span class="p">`: `<span class="p">`[`<span class="s2">`&#34;/FULL/PATH/TO/YOUR/docker-hub-mcp-server/dist/index.js&#34;`<span class="p">`, `<span class="s2">`&#34;--transport=stdio&#34;`<span class="p">`, `<span class="s2">`&#34;--username=YOUR_DOCKER_HUB_USERNAME&#34;`<span class="p">`],
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;env&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`        `<span class="nt">`&#34;HUB_PAT_TOKEN&#34;`<span class="p">`: `<span class="s2">`&#34;YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN&#34;
`<span class="line"><span class="cl">`      `<span class="p">`}
`<span class="line"><span class="cl">`    `<span class="p">`}
`<span class="line"><span class="cl">`  `<span class="p">`}
`<span class="line"><span class="cl">``<span class="p">`}`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>Where :</p>
<ul>
<li><code>YOUR_DOCKER_HUB_USERNAME</code> is your Docker Hub username.</li>
<li><code>YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN</code> is Docker Hub personal access token</li>
<li><code>/FULL/PATH/TO/YOUR/docker-hub-mcp-server</code> is the complete path to where you cloned the repository</li>
</ul>



Where :


* `YOUR_DOCKER_HUB_USERNAME` is your Docker Hub username.
* `YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN` is Docker Hub personal access token
* `/FULL/PATH/TO/YOUR/docker-hub-mcp-server` is the complete path to where you cloned the repository

    `</div>`

</div>
</div>


1. Save the configuration file and completely restart Claude Desktop for the changes to take effect.

## Usage with Visual Studio Code

1. Add the Docker Hub MCP Server configuration to your User Settings (JSON)
   file in Visual Studio Code. You can do this by opening the `Command Palette` and
   typing `Preferences: Open User Settings (JSON)`.

<div
  class="tabs"

    x-data="{ selected: 'For-public-repositories-only' }"

  aria-role="tabpanel"

<div aria-role="tablist" class="tablist">

    <button
        class="tab-item"
        :class="selected === 'For-public-repositories-only' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'For-public-repositories-only'"

    >
        For public repositories only`</button>`

    <button
        class="tab-item"
        :class="selected === 'For-authenticated-access' &&
          'border-blue border-b-4 dark:border-b-blue-600'"

    @click="selected = 'For-authenticated-access'"

    >
        For authenticated access`</button>`

</div>
  <div>


  
    `<div
        aria-role="tab"
        :class="selected !== 'For-public-repositories-only' && 'hidden'"
      >`
        <div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'ewogICJtY3BTZXJ2ZXJzIjogewogICAgImRvY2tlci1odWIiOiB7CiAgICAgICJjb21tYW5kIjogIm5vZGUiLAogICAgICAiYXJncyI6IFsiL0ZVTEwvUEFUSC9UTy9ZT1VSL2RvY2tlci1odWItbWNwLXNlcnZlci9kaXN0L2luZGV4LmpzIiwgIi0tdHJhbnNwb3J0PXN0ZGlvIl0KICAgIH0KICB9Cn0=', copying: false }"
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

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-json" data-lang="json"><span class="line">``<span class="cl"><span class="p">`{
`<span class="line"><span class="cl">`  `<span class="nt">`&#34;mcpServers&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`    `<span class="nt">`&#34;docker-hub&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;command&#34;`<span class="p">`: `<span class="s2">`&#34;node&#34;`<span class="p">`,
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;args&#34;`<span class="p">`: `<span class="p">`[`<span class="s2">`&#34;/FULL/PATH/TO/YOUR/docker-hub-mcp-server/dist/index.js&#34;`<span class="p">`, `<span class="s2">`&#34;--transport=stdio&#34;`<span class="p">`]
`<span class="line"><span class="cl">`    `<span class="p">`}
`<span class="line"><span class="cl">`  `<span class="p">`}
`<span class="line"><span class="cl">``<span class="p">`}`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>Where :</p>
<ul>
<li><code>/FULL/PATH/TO/YOUR/docker-hub-mcp-server</code> is the complete path to where you cloned the repository</li>
</ul>



Where :


* `/FULL/PATH/TO/YOUR/docker-hub-mcp-server` is the complete path to where you cloned the repository

    `</div>`

    `<div
        aria-role="tab"
        :class="selected !== 'For-authenticated-access' && 'hidden'"
      >`
        <div
  data-pagefind-ignore
  x-data
  x-ref="root"
  class="group mt-2 mb-4 flex w-full scroll-mt-2 flex-col items-start gap-4 rounded bg-gray-50 p-2 outline outline-1 outline-offset-[-1px] outline-gray-200 dark:bg-gray-900 dark:outline-gray-800"

<div class="relative w-full">

    `<div class="syntax-light dark:syntax-dark not-prose w-full">`
      <button
        x-data="{ code: 'ewogICJtY3BTZXJ2ZXJzIjogewogICAgImRvY2tlci1odWIiOiB7CiAgICAgICJjb21tYW5kIjogIm5vZGUiLAogICAgICAiYXJncyI6IFsiL0ZVTEwvUEFUSC9UTy9ZT1VSL2RvY2tlci1odWItbWNwLXNlcnZlci9kaXN0L2luZGV4LmpzIiwgIi0tdHJhbnNwb3J0PXN0ZGlvIl0sCiAgICAgICJlbnYiOiB7CiAgICAgICAgIkhVQl9VU0VSTkFNRSI6ICJZT1VSX0RPQ0tFUl9IVUJfVVNFUk5BTUUiLAogICAgICAgICJIVUJfUEFUX1RPS0VOIjogIllPVVJfRE9DS0VSX0hVQl9QRVJTT05BTF9BQ0NFU1NfVE9LRU4iCiAgICAgIH0KICAgIH0KICB9Cn0=', copying: false }"
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

    `<div class="highlight"><pre tabindex="0" class="chroma">``<code class="language-json" data-lang="json"><span class="line">``<span class="cl"><span class="p">`{
`<span class="line"><span class="cl">`  `<span class="nt">`&#34;mcpServers&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`    `<span class="nt">`&#34;docker-hub&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;command&#34;`<span class="p">`: `<span class="s2">`&#34;node&#34;`<span class="p">`,
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;args&#34;`<span class="p">`: `<span class="p">`[`<span class="s2">`&#34;/FULL/PATH/TO/YOUR/docker-hub-mcp-server/dist/index.js&#34;`<span class="p">`, `<span class="s2">`&#34;--transport=stdio&#34;`<span class="p">`],
`<span class="line"><span class="cl">`      `<span class="nt">`&#34;env&#34;`<span class="p">`: `<span class="p">`{
`<span class="line"><span class="cl">`        `<span class="nt">`&#34;HUB_USERNAME&#34;`<span class="p">`: `<span class="s2">`&#34;YOUR_DOCKER_HUB_USERNAME&#34;`<span class="p">`,
`<span class="line"><span class="cl">`        `<span class="nt">`&#34;HUB_PAT_TOKEN&#34;`<span class="p">`: `<span class="s2">`&#34;YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN&#34;
`<span class="line"><span class="cl">`      `<span class="p">`}
`<span class="line"><span class="cl">`    `<span class="p">`}
`<span class="line"><span class="cl">`  `<span class="p">`}
`<span class="line"><span class="cl">``<span class="p">`}`</code></pre>``</div>`

    `</div>`

</div>
</div>
<p>Where :</p>
<ul>
<li><code>YOUR_DOCKER_HUB_USERNAME</code> is your Docker Hub username.</li>
<li><code>YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN</code> is Docker Hub personal access token</li>
<li><code>/FULL/PATH/TO/YOUR/docker-hub-mcp-server</code> is the complete path to where you cloned the repository</li>
</ul>



Where :


* `YOUR_DOCKER_HUB_USERNAME` is your Docker Hub username.
* `YOUR_DOCKER_HUB_PERSONAL_ACCESS_TOKEN` is Docker Hub personal access token
* `/FULL/PATH/TO/YOUR/docker-hub-mcp-server` is the complete path to where you cloned the repository

    `</div>`

</div>
</div>


1. Open the `Command Palette` and type `MCP: List Servers`.
2. Select `docker-hub` and select `Start Server`.

## Using other clients

To integrate the Docker Hub MCP Server into your own development
environment, see the source code and installation instructions on the
[`hub-mcp` GitHub repository](https://github.com/docker/hub-mcp).

## Usage examples

This section provides task-oriented examples for common operations with Docker Hub
tools.

### Finding images

```console
# Search for official images
$ docker ai "Search for official nginx images on Docker Hub"

# Search for lightweight images to reduce deployment size and improve performance
$ docker ai "Search for minimal Node.js images with small footprint"

# Get the most recent tag of a base image
$ docker ai "Show me the latest tag details for go"

# Find a production-ready database with enterprise features and reliability
$ docker ai "Search for production ready database images"

# Compare Ubuntu versions to choose the right one for my project
$ docker ai "Help me find the right Ubuntu version for my project"
```

### Repository management

```console
# Create a repository
$ docker ai "Create a repository in my namespace"

# List all repositories in my namespace
$ docker ai "List all repositories in my namespace"

# Find the largest repository in my namespace
$ docker ai "Which of my repositories takes up the most space?"

# Find repositories that haven't been updated recently
$ docker ai "Which of my repositories haven't had any pushes in the last 60 days?"

# Find which repositories are currently active and being used
$ docker ai "Show me my most recently updated repositories"

# Get details about a repository
$ docker ai "Show me information about my '<repository-name>' repository"
```

### Pull/push images

```console
# Pull latest PostgreSQL version
$ docker ai "Pull the latest postgres image"

# Push image to your Docker Hub repository
$ docker ai "Push my <image-name> to my <repository-name> repository"
```

### Tag management

```console
# List all tags for a repository
$ $ docker ai "Show me all tags for my '<repository-name>' repository"

# Find the most recently pushed tag
$ docker ai "What's the most recent tag pushed to my '<repository-name>' repository?"

# List tags with architecture filtering
$ docker ai "List tags for in the '<repository-name>' repository that support amd64 architecture"

# Get detailed information about a specific tag
$ docker ai "Show me details about the '<tag-name>' tag in the '<repository-name>' repository"

# Check if a specific tag exists
$ docker ai "Check if version 'v1.2.0' exists for my 'my-web-app' repository"
```

### Docker Hardened Images

```console
# List available hardened images
$ docker ai "What is the most secure image I can use to run a node.js application?"

# Convert Dockerfile to use a hardened image
$ docker ai "Can you help me update my Dockerfile to use a docker hardened image instead of the current one"
```

> [!NOTE]
> To access Docker Hardened Images, a subscription is required. If you're interested in using Docker Hardened Images, visit [Docker Hardened Images](https://www.docker.com/products/hardened-images/).

## Reference

This section provides a comprehensive listing of the tools you can find
in the Docker Hub MCP Server.

### Docker Hub MCP server tools

Tools to interact with your Docker repositories and discover content on Docker Hub.

| Name                               | Description                                                                                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `check-repository`               | Check repository                                                                                              |
| `check-repository-tag`           | Check repository tag                                                                                          |
| `check-repository-tags`          | Check repository tags                                                                                         |
| `create-repository`              | Creates a new repository                                                                                      |
| `docker-hardened-images`         | Lists available[Docker Hardened Images](https://www.docker.com/products/hardened-images/) in specified namespace |
| `get-namespaces`                 | Get organizations/namespaces for a user                                                                       |
| `get-repository-dockerfile`      | Gets Dockerfile for repository                                                                                |
| `get-repository-info`            | Gets repository info                                                                                          |
| `list-repositories-by-namespace` | Lists repositories under namespace                                                                            |
| `list-repository-tags`           | List repository tags                                                                                          |
| `read-repository-tag`            | Read repository tag                                                                                           |
| `search`                         | Search content on Docker Hub                                                                                  |
| `set-repository-dockerfile`      | Sets Dockerfile for repository                                                                                |
| `update-repository-info`         | Updates repository info                                                                                       |
