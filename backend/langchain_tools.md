# Brave Search

This notebook goes over how to use the Brave Search tool.
Go to the [Brave Website](https://brave.com/search/api/) to sign up for a free account and get an API key.

```python  theme={null}
pip install -qU langchain-community
```

```python  theme={null}
from langchain_community.tools import BraveSearch
```

```python  theme={null}
api_key = "API KEY"
```

```python  theme={null}
tool = BraveSearch.from_api_key(api_key=api_key, search_kwargs={"count": 3})

# or if you want to get the api key from environment variable BRAVE_SEARCH_API_KEY, and leave search_kwargs empty
# tool = BraveSearch()

# or if you want to provide just the api key, and leave search_kwargs empty
# tool = BraveSearch.from_api_key(api_key=api_key)

# or if you want to provide just the search_kwargs and read the api key from the BRAVE_SEARCH_API_KEY environment variable
# tool = BraveSearch.from_search_kwargs(search_kwargs={"count": 3})
```

```python  theme={null}
tool.run("obama middle name")
```

```output  theme={null}
'[{"title": "Obama\'s Middle Name -- My Last Name -- is \'Hussein.\' So?", "link": "https://www.cair.com/cair_in_the_news/obamas-middle-name-my-last-name-is-hussein-so/", "snippet": "I wasn\\u2019t sure whether to laugh or cry a few days back listening to radio talk show host Bill Cunningham repeatedly scream Barack <strong>Obama</strong>\\u2019<strong>s</strong> <strong>middle</strong> <strong>name</strong> \\u2014 my last <strong>name</strong> \\u2014 as if he had anti-Muslim Tourette\\u2019s. \\u201cHussein,\\u201d Cunningham hissed like he was beckoning Satan when shouting the ..."}, {"title": "What\'s up with Obama\'s middle name? - Quora", "link": "https://www.quora.com/Whats-up-with-Obamas-middle-name", "snippet": "Answer (1 of 15): A better question would be, \\u201cWhat\\u2019s up with <strong>Obama</strong>\\u2019s first <strong>name</strong>?\\u201d President Barack Hussein <strong>Obama</strong>\\u2019s father\\u2019s <strong>name</strong> was Barack Hussein <strong>Obama</strong>. He was <strong>named</strong> after his father. Hussein, <strong>Obama</strong>\\u2019<strong>s</strong> <strong>middle</strong> <strong>name</strong>, is a very common Arabic <strong>name</strong>, meaning &quot;good,&quot; &quot;handsome,&quot; or ..."}, {"title": "Barack Obama | Biography, Parents, Education, Presidency, Books, ...", "link": "https://www.britannica.com/biography/Barack-Obama", "snippet": "Barack <strong>Obama</strong>, in full Barack Hussein <strong>Obama</strong> II, (born August 4, 1961, Honolulu, Hawaii, U.S.), 44th president of the United States (2009\\u201317) and the first African American to hold the office. Before winning the presidency, <strong>Obama</strong> represented Illinois in the U.S."}]'
```

```python  theme={null}
```

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/brave_search.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# Brave Search

This notebook goes over how to use the Brave Search tool.
Go to the [Brave Website](https://brave.com/search/api/) to sign up for a free account and get an API key.

```python  theme={null}
pip install -qU langchain-community
```

```python  theme={null}
from langchain_community.tools import BraveSearch
```

```python  theme={null}
api_key = "API KEY"
```

```python  theme={null}
tool = BraveSearch.from_api_key(api_key=api_key, search_kwargs={"count": 3})

# or if you want to get the api key from environment variable BRAVE_SEARCH_API_KEY, and leave search_kwargs empty
# tool = BraveSearch()

# or if you want to provide just the api key, and leave search_kwargs empty
# tool = BraveSearch.from_api_key(api_key=api_key)

# or if you want to provide just the search_kwargs and read the api key from the BRAVE_SEARCH_API_KEY environment variable
# tool = BraveSearch.from_search_kwargs(search_kwargs={"count": 3})
```

```python  theme={null}
tool.run("obama middle name")
```

```output  theme={null}
'[{"title": "Obama\'s Middle Name -- My Last Name -- is \'Hussein.\' So?", "link": "https://www.cair.com/cair_in_the_news/obamas-middle-name-my-last-name-is-hussein-so/", "snippet": "I wasn\\u2019t sure whether to laugh or cry a few days back listening to radio talk show host Bill Cunningham repeatedly scream Barack <strong>Obama</strong>\\u2019<strong>s</strong> <strong>middle</strong> <strong>name</strong> \\u2014 my last <strong>name</strong> \\u2014 as if he had anti-Muslim Tourette\\u2019s. \\u201cHussein,\\u201d Cunningham hissed like he was beckoning Satan when shouting the ..."}, {"title": "What\'s up with Obama\'s middle name? - Quora", "link": "https://www.quora.com/Whats-up-with-Obamas-middle-name", "snippet": "Answer (1 of 15): A better question would be, \\u201cWhat\\u2019s up with <strong>Obama</strong>\\u2019s first <strong>name</strong>?\\u201d President Barack Hussein <strong>Obama</strong>\\u2019s father\\u2019s <strong>name</strong> was Barack Hussein <strong>Obama</strong>. He was <strong>named</strong> after his father. Hussein, <strong>Obama</strong>\\u2019<strong>s</strong> <strong>middle</strong> <strong>name</strong>, is a very common Arabic <strong>name</strong>, meaning &quot;good,&quot; &quot;handsome,&quot; or ..."}, {"title": "Barack Obama | Biography, Parents, Education, Presidency, Books, ...", "link": "https://www.britannica.com/biography/Barack-Obama", "snippet": "Barack <strong>Obama</strong>, in full Barack Hussein <strong>Obama</strong> II, (born August 4, 1961, Honolulu, Hawaii, U.S.), 44th president of the United States (2009\\u201317) and the first African American to hold the office. Before winning the presidency, <strong>Obama</strong> represented Illinois in the U.S."}]'
```

```python  theme={null}
```

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/brave_search.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# Github Toolkit

The `Github` toolkit contains tools that enable an LLM agent to interact with a github repository.
The tool is a wrapper for the [PyGitHub](https://github.com/PyGithub/PyGithub) library.

For detailed documentation of all GithubToolkit features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.github.toolkit.GitHubToolkit.html).

## Setup

At a high-level, we will:

1. Install the pygithub library
2. Create a Github app
3. Set your environmental variables
4. Pass the tools to your agent with `toolkit.get_tools()`

To enable automated tracing of individual tools, set your [LangSmith](https://docs.smith.langchain.com/) API key:

```python  theme={null}
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
os.environ["LANGSMITH_TRACING"] = "true"
```

### Installation

#### 1. Install dependencies

This integration is implemented in `langchain-community`. We will also need the `pygithub` dependency:

```python  theme={null}
pip install -qU  pygithub langchain-community
```

#### 2. Create a Github app

[Follow the instructions here](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app) to create and register a Github app. Make sure your app has the following [repository permissions:](https://docs.github.com/en/rest/overview/permissions-required-for-github-apps?apiVersion=2022-11-28)

* Commit statuses (read only)
* Contents (read and write)
* Issues (read and write)
* Metadata (read only)
* Pull requests (read and write)

Once the app has been registered, you must give your app permission to access each of the repositories you whish it to act upon. Use the App settings on [github.com here](https://github.com/settings/installations).

#### 3. Set environment variables

Before initializing your agent, the following environment variables need to be set:

* **GITHUB\_APP\_ID**- A six digit number found in your app's general settings
* **GITHUB\_APP\_PRIVATE\_KEY**- The location of your app's private key .pem file, or the full text of that file as a string.
* **GITHUB\_REPOSITORY**- The name of the Github repository you want your bot to act upon. Must follow the format \{username}/\{repo-name}. *Make sure the app has been added to this repository first!*
* Optional: **GITHUB\_BRANCH**- The branch where the bot will make its commits. Defaults to `repo.default_branch`.
* Optional: **GITHUB\_BASE\_BRANCH**- The base branch of your repo upon which PRs will based from. Defaults to `repo.default_branch`.

```python  theme={null}
import getpass
import os

for env_var in [
    "GITHUB_APP_ID",
    "GITHUB_APP_PRIVATE_KEY",
    "GITHUB_REPOSITORY",
]:
    if not os.getenv(env_var):
        os.environ[env_var] = getpass.getpass()
```

## Instantiation

Now we can instantiate our toolkit:

```python  theme={null}
from langchain_community.agent_toolkits.github.toolkit import GitHubToolkit
from langchain_community.utilities.github import GitHubAPIWrapper

github = GitHubAPIWrapper()
toolkit = GitHubToolkit.from_github_api_wrapper(github)
```

## Tools

View available tools:

```python  theme={null}
tools = toolkit.get_tools()

for tool in tools:
    print(tool.name)
```

```output  theme={null}
Get Issues
Get Issue
Comment on Issue
List open pull requests (PRs)
Get Pull Request
Overview of files included in PR
Create Pull Request
List Pull Requests' Files
Create File
Read File
Update File
Delete File
Overview of existing files in Main branch
Overview of files in current working branch
List branches in this repository
Set active branch
Create a new branch
Get files from a directory
Search issues and pull requests
Search code
Create review request
```

The purpose of these tools is as follows:

Each of these steps will be explained in great detail below.

1. **Get Issues**- fetches issues from the repository.

2. **Get Issue**- fetches details about a specific issue.

3. **Comment on Issue**- posts a comment on a specific issue.

4. **Create Pull Request**- creates a pull request from the bot's working branch to the base branch.

5. **Create File**- creates a new file in the repository.

6. **Read File**- reads a file from the repository.

7. **Update File**- updates a file in the repository.

8. **Delete File**- deletes a file from the repository.

## Include release tools

By default, the toolkit does not include release-related tools. You can include them by setting `include_release_tools=True` when initializing the toolkit:

```python  theme={null}
toolkit = GitHubToolkit.from_github_api_wrapper(github, include_release_tools=True)
```

Settings `include_release_tools=True` will include the following tools:

* **Get Latest Release**- fetches the latest release from the repository.

* **Get Releases**- fetches the latest 5 releases from the repository.

* **Get Release**- fetches a specific release from the repository by tag name, e.g. `v1.0.0`.

## Use within an agent

We will need a LLM or chat model:

<ChatModelTabs customVarName="llm" />

```python  theme={null}
# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

Initialize the agent with a subset of tools:

```python  theme={null}
from langchain.agents import create_agent


tools = [tool for tool in toolkit.get_tools() if tool.name == "Get Issue"]
assert len(tools) == 1
tools[0].name = "get_issue"

agent_executor = create_agent(llm, tools)
```

And issue it a query:

```python  theme={null}
example_query = "What is the title of issue 24888?"

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
```

```output  theme={null}
================================ Human Message =================================

What is the title of issue 24888?
================================== Ai Message ==================================
Tool Calls:
  get_issue (call_iSYJVaM7uchfNHOMJoVPQsOi)
 Call ID: call_iSYJVaM7uchfNHOMJoVPQsOi
  Args:
    issue_number: 24888
================================= Tool Message =================================
Name: get_issue

{"number": 24888, "title": "Standardize KV-Store Docs", "body": "To make our KV-store integrations as easy to use as possible we need to make sure the docs for them are thorough and standardized. There are two parts to this: updating the KV-store docstrings and updating the actual integration docs.\r\n\r\nThis needs to be done for each KV-store integration, ideally with one PR per KV-store.\r\n\r\nRelated to broader issues #21983 and #22005.\r\n\r\n## Docstrings\r\nEach KV-store class docstring should have the sections shown in the [Appendix](#appendix) below. The sections should have input and output code blocks when relevant.\r\n\r\nTo build a preview of the API docs for the package you're working on run (from root of repo):\r\n\r\n\`\`\`shell\r\nmake api_docs_clean; make api_docs_quick_preview API_PKG=openai\r\n\`\`\`\r\n\r\nwhere `API_PKG=` should be the parent directory that houses the edited package (e.g. community, openai, anthropic, huggingface, together, mistralai, groq, fireworks, etc.). This should be quite fast for all the partner packages.\r\n\r\n## Doc pages\r\nEach KV-store [docs page](https://python.langchain.com/docs/integrations/stores/) should follow [this template](https://github.com/langchain-ai/langchain/blob/master/libs/cli/langchain_cli/integration_template/docs/kv_store.ipynb).\r\n\r\nHere is an example: https://python.langchain.com/docs/integrations/stores/in_memory/\r\n\r\nYou can use the `langchain-cli` to quickly get started with a new chat model integration docs page (run from root of repo):\r\n\r\n\`\`\`shell\r\npoetry run pip install -e libs/cli\r\npoetry run langchain-cli integration create-doc --name \"foo-bar\" --name-class FooBar --component-type kv_store --destination-dir ./docs/docs/integrations/stores/\r\n\`\`\`\r\n\r\nwhere `--name` is the integration package name without the \"langchain-\" prefix and `--name-class` is the class name without the \"ByteStore\" suffix. This will create a template doc with some autopopulated fields at docs/docs/integrations/stores/foo_bar.ipynb.\r\n\r\nTo build a preview of the docs you can run (from root):\r\n\r\n\`\`\`shell\r\nmake docs_clean\r\nmake docs_build\r\ncd docs/build/output-new\r\nyarn\r\nyarn start\r\n\`\`\`\r\n\r\n## Appendix\r\nExpected sections for the KV-store class docstring.\r\n\r\n\`\`\`python\r\n    \"\"\"__ModuleName__ completion KV-store integration.\r\n\r\n    # TODO: Replace with relevant packages, env vars.\r\n    Setup:\r\n        Install `__package_name__` and set environment variable `__MODULE_NAME___API_KEY`.\r\n\r\n        .. code-block:: bash\r\n\r\n            pip install -U __package_name__\r\n            export __MODULE_NAME___API_KEY=\"your-api-key\"\r\n\r\n    # TODO: Populate with relevant params.\r\n    Key init args \u2014 client params:\r\n        api_key: Optional[str]\r\n            __ModuleName__ API key. If not passed in will be read from env var __MODULE_NAME___API_KEY.\r\n\r\n    See full list of supported init args and their descriptions in the params section.\r\n\r\n    # TODO: Replace with relevant init params.\r\n    Instantiate:\r\n        .. code-block:: python\r\n\r\n            from __module_name__ import __ModuleName__ByteStore\r\n\r\n            kv_store = __ModuleName__ByteStore(\r\n                # api_key=\"...\",\r\n                # other params...\r\n            )\r\n\r\n    Set keys:\r\n        .. code-block:: python\r\n\r\n            kv_pairs = [\r\n                [\"key1\", \"value1\"],\r\n                [\"key2\", \"value2\"],\r\n            ]\r\n\r\n            kv_store.mset(kv_pairs)\r\n\r\n        .. code-block:: python\r\n\r\n    Get keys:\r\n        .. code-block:: python\r\n\r\n            kv_store.mget([\"key1\", \"key2\"])\r\n\r\n        .. code-block:: python\r\n\r\n            # TODO: Example output.\r\n\r\n    Delete keys:\r\n        ..code-block:: python\r\n\r\n            kv_store.mdelete([\"key1\", \"key2\"])\r\n\r\n        ..code-block:: python\r\n    \"\"\"  # noqa: E501\r\n\`\`\`", "comments": "[]", "opened_by": "jacoblee93"}
================================== Ai Message ==================================

The title of issue 24888 is "Standardize KV-Store Docs".
```

***

## API reference

For detailed documentation of all `GithubToolkit` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.github.toolkit.GitHubToolkit.html).

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/github.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# Gmail Toolkit

This will help you get started with the Gmail [toolkit](/oss/python/langchain/tools#toolkits). This toolkit interacts with the Gmail API to read messages, draft and send messages, and more. For detailed documentation of all GmailToolkit features and configurations head to the [API reference](https://python.langchain.com/api_reference/google_community/gmail/langchain_google_community.gmail.toolkit.GmailToolkit.html).

## Setup

To use this toolkit, you will need to set up your credentials explained in the [Gmail API docs](https://developers.google.com/gmail/api/quickstart/python#authorize_credentials_for_a_desktop_application). Once you've downloaded the `credentials.json` file, you can start using the Gmail API.

### Installation

This toolkit lives in the `langchain-google-community` package. We'll need the `gmail` extra:

```python  theme={null}
pip install -qU langchain-google-community\[gmail\]
```

To enable automated tracing of individual tools, set your [LangSmith](https://docs.smith.langchain.com/) API key:

```python  theme={null}
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
```

## Instantiation

By default the toolkit reads the local `credentials.json` file. You can also manually provide a `Credentials` object.

```python  theme={null}
from langchain_google_community import GmailToolkit

toolkit = GmailToolkit()
```

### Customizing Authentication

Behind the scenes, a `googleapi` resource is created using the following methods.
you can manually build a `googleapi` resource for more auth control.

```python  theme={null}
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

# Can review scopes here https://developers.google.com/gmail/api/auth/scopes
# For instance, readonly scope is 'https://www.googleapis.com/auth/gmail.readonly'
credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)
```

## Tools

View available tools:

```python  theme={null}
tools = toolkit.get_tools()
tools
```

```output  theme={null}
[GmailCreateDraft(api_resource=<googleapiclient.discovery.Resource object at 0x1094509d0>),
 GmailSendMessage(api_resource=<googleapiclient.discovery.Resource object at 0x1094509d0>),
 GmailSearch(api_resource=<googleapiclient.discovery.Resource object at 0x1094509d0>),
 GmailGetMessage(api_resource=<googleapiclient.discovery.Resource object at 0x1094509d0>),
 GmailGetThread(api_resource=<googleapiclient.discovery.Resource object at 0x1094509d0>)]
```

* [GmailCreateDraft](https://python.langchain.com/api_reference/google_community/gmail/langchain_google_community.gmail.create_draft.GmailCreateDraft.html)
* [GmailSendMessage](https://python.langchain.com/api_reference/google_community/gmail/langchain_google_community.gmail.send_message.GmailSendMessage.html)
* [GmailSearch](https://python.langchain.com/api_reference/google_community/gmail/langchain_google_community.gmail.search.GmailSearch.html)
* [GmailGetMessage](https://python.langchain.com/api_reference/google_community/gmail/langchain_google_community.gmail.get_message.GmailGetMessage.html)
* [GmailGetThread](https://python.langchain.com/api_reference/google_community/gmail/langchain_google_community.gmail.get_thread.GmailGetThread.html)

## Use within an agent

Below we show how to incorporate the toolkit into an [agent](/oss/python/langchain/agents).

We will need a LLM or chat model:

<ChatModelTabs customVarName="llm" />

```python  theme={null}
# | output: false
# | echo: false

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

```python  theme={null}
from langchain.agents import create_agent


agent_executor = create_agent(llm, tools)
```

```python  theme={null}
example_query = "Draft an email to fake@fake.com thanking them for coffee."

events = agent_executor.stream(
    {"messages": [("user", example_query)]},
    stream_mode="values",
)
for event in events:
    event["messages"][-1].pretty_print()
```

```output  theme={null}
================================ Human Message =================================

Draft an email to fake@fake.com thanking them for coffee.
================================== Ai Message ==================================
Tool Calls:
  create_gmail_draft (call_slGkYKZKA6h3Mf1CraUBzs6M)
 Call ID: call_slGkYKZKA6h3Mf1CraUBzs6M
  Args:
    message: Dear Fake,

I wanted to take a moment to thank you for the coffee yesterday. It was a pleasure catching up with you. Let's do it again soon!

Best regards,
[Your Name]
    to: ['fake@fake.com']
    subject: Thank You for the Coffee
================================= Tool Message =================================
Name: create_gmail_draft

Draft created. Draft Id: r-7233782721440261513
================================== Ai Message ==================================

I have drafted an email to fake@fake.com thanking them for the coffee. You can review and send it from your email draft with the subject "Thank You for the Coffee".
```

***

## API reference

For detailed documentation of all `GmailToolkit` features and configurations head to the [API reference](https://python.langchain.com/api_reference/community/agent_toolkits/langchain_community.agent_toolkits.gmail.toolkit.GmailToolkit.html).

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/gmail.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# PlayWright Browser Toolkit

> [Playwright](https://github.com/microsoft/playwright) is an open-source automation tool developed by `Microsoft` that allows you to programmatically control and automate web browsers. It is designed for end-to-end testing, scraping, and automating tasks across various web browsers such as `Chromium`, `Firefox`, and `WebKit`.

This toolkit is used to interact with the browser. While other tools (like the `Requests` tools) are fine for static sites, `PlayWright Browser` toolkits let your agent navigate the web and interact with dynamically rendered sites.

Some tools bundled within the `PlayWright Browser` toolkit include:

* `NavigateTool` (navigate\_browser) - navigate to a URL
* `NavigateBackTool` (previous\_page) - wait for an element to appear
* `ClickTool` (click\_element) - click on an element (specified by selector)
* `ExtractTextTool` (extract\_text) - use beautiful soup to extract text from the current web page
* `ExtractHyperlinksTool` (extract\_hyperlinks) - use beautiful soup to extract hyperlinks from the current web page
* `GetElementsTool` (get\_elements) - select elements by CSS selector
* `CurrentPageTool` (current\_page) - get the current page URL

```python  theme={null}
pip install -qU  playwright > /dev/null
pip install -qU  lxml

# If this is your first time using playwright, you'll have to install a browser executable.
# Running `playwright install` by default installs a chromium browser executable.
# playwright install
```

```output  theme={null}
[notice] A new release of pip is available: 24.0 -> 24.2
[notice] To update, run: pip install -U pip
Note: you may need to restart the kernel to use updated packages.

[notice] A new release of pip is available: 24.0 -> 24.2
[notice] To update, run: pip install -U pip
Note: you may need to restart the kernel to use updated packages.
```

```python  theme={null}
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
```

Async function to create context and launch browser:

```python  theme={null}
from langchain_community.tools.playwright.utils import (
    create_async_playwright_browser,  # A synchronous browser is available, though it isn't compatible with jupyter.\n",   },
)
```

```python  theme={null}
# This import is required only for jupyter notebooks, since they have their own eventloop
import nest_asyncio

nest_asyncio.apply()
```

## Instantiating a Browser Toolkit

It's always recommended to instantiate using the from\_browser method so that the browser context is properly initialized and managed, ensuring seamless interaction and resource optimization.

```python  theme={null}
async_browser = create_async_playwright_browser()
toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=async_browser)
tools = toolkit.get_tools()
tools
```

```output  theme={null}
[ClickTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>),
 NavigateTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>),
 NavigateBackTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>),
 ExtractTextTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>),
 ExtractHyperlinksTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>),
 GetElementsTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>),
 CurrentWebPageTool(async_browser=<Browser type=<BrowserType name=chromium executable_path=/Users/isaachershenson/Library/Caches/ms-playwright/chromium-1124/chrome-mac/Chromium.app/Contents/MacOS/Chromium> version=127.0.6533.17>)]
```

```python  theme={null}
tools_by_name = {tool.name: tool for tool in tools}
navigate_tool = tools_by_name["navigate_browser"]
get_elements_tool = tools_by_name["get_elements"]
```

```python  theme={null}
await navigate_tool.arun(
    {"url": "https://web.archive.org/web/20230428133211/https://cnn.com/world"}
)
```

```output  theme={null}
'Navigating to https://web.archive.org/web/20230428133211/https://cnn.com/world returned status code 200'
```

```python  theme={null}
# The browser is shared across tools, so the agent can interact in a stateful manner
await get_elements_tool.arun(
    {"selector": ".container__headline", "attributes": ["innerText"]}
)
```

```output  theme={null}
'[{"innerText": "These Ukrainian veterinarians are risking their lives to care for dogs and cats in the war zone"}, {"innerText": "Life in the ocean’s ‘twilight zone’ could disappear due to the climate crisis"}, {"innerText": "Clashes renew in West Darfur as food and water shortages worsen in Sudan violence"}, {"innerText": "Thai policeman’s wife investigated over alleged murder and a dozen other poison cases"}, {"innerText": "American teacher escaped Sudan on French evacuation plane, with no help offered back home"}, {"innerText": "Dubai’s emerging hip-hop scene is finding its voice"}, {"innerText": "How an underwater film inspired a marine protected area off Kenya’s coast"}, {"innerText": "The Iranian drones deployed by Russia in Ukraine are powered by stolen Western technology, research reveals"}, {"innerText": "India says border violations erode ‘entire basis’ of ties with China"}, {"innerText": "Australian police sift through 3,000 tons of trash for missing woman’s remains"}, {"innerText": "As US and Philippine defense ties grow, China warns over Taiwan tensions"}, {"innerText": "Don McLean offers duet with South Korean president who sang ‘American Pie’ to Biden"}, {"innerText": "Almost two-thirds of elephant habitat lost across Asia, study finds"}, {"innerText": "‘We don’t sleep … I would call it fainting’: Working as a doctor in Sudan’s crisis"}, {"innerText": "Kenya arrests second pastor to face criminal charges ‘related to mass killing of his followers’"}, {"innerText": "Russia launches deadly wave of strikes across Ukraine"}, {"innerText": "Woman forced to leave her forever home or ‘walk to your death’ she says"}, {"innerText": "U.S. House Speaker Kevin McCarthy weighs in on Disney-DeSantis feud"}, {"innerText": "Two sides agree to extend Sudan ceasefire"}, {"innerText": "Spanish Leopard 2 tanks are on their way to Ukraine, defense minister confirms"}, {"innerText": "Flambéed pizza thought to have sparked deadly Madrid restaurant fire"}, {"innerText": "Another bomb found in Belgorod just days after Russia accidentally struck the city"}, {"innerText": "A Black teen’s murder sparked a crisis over racism in British policing. Thirty years on, little has changed"}, {"innerText": "Belgium destroys shipment of American beer after taking issue with ‘Champagne of Beer’ slogan"}, {"innerText": "UK Prime Minister Rishi Sunak rocked by resignation of top ally Raab over bullying allegations"}, {"innerText": "Iran’s Navy seizes Marshall Islands-flagged ship"}, {"innerText": "A divided Israel stands at a perilous crossroads on its 75th birthday"}, {"innerText": "Palestinian reporter breaks barriers by reporting in Hebrew on Israeli TV"}, {"innerText": "One-fifth of water pollution comes from textile dyes. But a shellfish-inspired solution could clean it up"}, {"innerText": "‘People sacrificed their lives for just\xa010 dollars’: At least 78 killed in Yemen crowd surge"}, {"innerText": "Israeli police say two men shot near Jewish tomb in Jerusalem in suspected ‘terror attack’"}, {"innerText": "King Charles III’s coronation: Who’s performing at the ceremony"}, {"innerText": "The week in 33 photos"}, {"innerText": "Hong Kong’s endangered turtles"}, {"innerText": "In pictures: Britain’s Queen Camilla"}, {"innerText": "Catastrophic drought that’s pushed millions into crisis made 100 times more likely by climate change, analysis finds"}, {"innerText": "For years, a UK mining giant was untouchable in Zambia for pollution until a former miner’s son took them on"}, {"innerText": "Former Sudanese minister Ahmed Haroun wanted on war crimes charges freed from Khartoum prison"}, {"innerText": "WHO warns of ‘biological risk’ after Sudan fighters seize lab, as violence mars US-brokered ceasefire"}, {"innerText": "How Colombia’s Petro, a former leftwing guerrilla, found his opening in Washington"}, {"innerText": "Bolsonaro accidentally created Facebook post questioning Brazil election results, say his attorneys"}, {"innerText": "Crowd kills over a dozen suspected gang members in Haiti"}, {"innerText": "Thousands of tequila bottles containing liquid meth seized"}, {"innerText": "Why send a US stealth submarine to South Korea – and tell the world about it?"}, {"innerText": "Fukushima’s fishing industry survived a nuclear disaster. 12 years on, it fears Tokyo’s next move may finish it off"}, {"innerText": "Singapore executes man for trafficking two pounds of cannabis"}, {"innerText": "Conservative Thai party looks to woo voters with promise to legalize sex toys"}, {"innerText": "Inside the Italian village being repopulated by Americans"}, {"innerText": "Strikes, soaring airfares and yo-yoing hotel fees: A traveler’s guide to the coronation"}, {"innerText": "A year in Azerbaijan: From spring’s Grand Prix to winter ski adventures"}, {"innerText": "The bicycle mayor peddling a two-wheeled revolution in Cape Town"}, {"innerText": "Tokyo ramen shop bans customers from using their phones while eating"}, {"innerText": "South African opera star will perform at coronation of King Charles III"}, {"innerText": "Luxury loot under the hammer: France auctions goods seized from drug dealers"}, {"innerText": "Judy Blume’s books were formative for generations of readers. Here’s why they endure"}, {"innerText": "Craft, salvage and sustainability take center stage at Milan Design Week"}, {"innerText": "Life-sized chocolate King Charles III sculpture unveiled to celebrate coronation"}, {"innerText": "Severe storms to strike the South again as millions in Texas could see damaging winds and hail"}, {"innerText": "The South is in the crosshairs of severe weather again, as the multi-day threat of large hail and tornadoes continues"}, {"innerText": "Spring snowmelt has cities along the Mississippi bracing for flooding in homes and businesses"}, {"innerText": "Know the difference between a tornado watch, a tornado warning and a tornado emergency"}, {"innerText": "Reporter spotted familiar face covering Sudan evacuation. See what happened next"}, {"innerText": "This country will soon become the world’s most populated"}, {"innerText": "April 27, 2023 - Russia-Ukraine news"}, {"innerText": "‘Often they shoot at each other’: Ukrainian drone operator details chaos in Russian ranks"}, {"innerText": "Hear from family members of Americans stuck in Sudan frustrated with US response"}, {"innerText": "U.S. talk show host Jerry Springer dies at 79"}, {"innerText": "Bureaucracy stalling at least one family’s evacuation from Sudan"}, {"innerText": "Girl to get life-saving treatment for rare immune disease"}, {"innerText": "Haiti’s crime rate more than doubles in a year"}, {"innerText": "Ocean census aims to discover 100,000 previously unknown marine species"}, {"innerText": "Wall Street Journal editor discusses reporter’s arrest in Moscow"}, {"innerText": "Can Tunisia’s democracy be saved?"}, {"innerText": "Yasmeen Lari, ‘starchitect’ turned social engineer, wins one of architecture’s most coveted prizes"}, {"innerText": "A massive, newly restored Frank Lloyd Wright mansion is up for sale"}, {"innerText": "Are these the most sustainable architectural projects in the world?"}, {"innerText": "Step inside a $72 million London townhouse in a converted army barracks"}, {"innerText": "A 3D-printing company is preparing to build on the lunar surface. But first, a moonshot at home"}, {"innerText": "Simona Halep says ‘the stress is huge’ as she battles to return to tennis following positive drug test"}, {"innerText": "Barcelona reaches third straight Women’s Champions League final with draw against Chelsea"}, {"innerText": "Wrexham: An intoxicating tale of Hollywood glamor and sporting romance"}, {"innerText": "Shohei Ohtani comes within inches of making yet more MLB history in Angels win"}, {"innerText": "This CNN Hero is recruiting recreational divers to help rebuild reefs in Florida one coral at a time"}, {"innerText": "This CNN Hero offers judgment-free veterinary care for the pets of those experiencing homelessness"}, {"innerText": "Don’t give up on milestones: A CNN Hero’s message for Autism Awareness Month"}, {"innerText": "CNN Hero of the Year Nelly Cheboi returned to Kenya with plans to lift more students out of poverty"}]'
```

```python  theme={null}
# If the agent wants to remember the current webpage, it can use the `current_webpage` tool
await tools_by_name["current_webpage"].arun({})
```

```output  theme={null}
'https://web.archive.org/web/20230428133211/https://cnn.com/world'
```

## Use within an Agent

Several of the browser tools are `StructuredTool`'s, meaning they expect multiple arguments. These aren't compatible (out of the box) with agents older than the `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION`

```python  theme={null}
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent


model = ChatAnthropic(
    model_name="claude-haiku-4-5-20251001", temperature=0
)  # or any other LLM, e.g., ChatOpenAI(), OpenAI()

agent_chain = create_agent(model=model, tools=tools)
```

```python  theme={null}
result = await agent_chain.ainvoke(
    {"messages": [("user", "What are the headers on langchain.com?")]}
)
print(result)
```

```output  theme={null}
> Entering new AgentExecutor chain...
Thought: To find the headers on langchain.com, I will navigate to the website and extract the text.

Action:
\`\`\`
{
  "action": "navigate_browser",
  "action_input": "https://langchain.com"
}
\`\`\`


Observation: Navigating to https://langchain.com returned status code 200
Thought:Okay, let's find the headers on the langchain.com website.

Action:
\`\`\`
{
  "action": "extract_text",
  "action_input": {}
}
\`\`\`


Observation: LangChain We value your privacy We use cookies to analyze our traffic. By clicking "Accept All", you consent to our use of cookies. Privacy Policy Customize Reject All Accept All Customize Consent Preferences We may use cookies to help you navigate efficiently and perform certain functions. You will find detailed information about all cookies under each consent category below. The cookies that are categorized as "Necessary" are stored on your browser as they are essential for enabling the basic functionalities of the site.... Show more Necessary Always Active Necessary cookies are required to enable the basic features of this site, such as providing secure log-in or adjusting your consent preferences. These cookies do not store any personally identifiable data. Functional Functional cookies help perform certain functionalities like sharing the content of the website on social media platforms, collecting feedback, and other third-party features. Analytics Analytical cookies are used to understand how visitors interact with the website. These cookies help provide information on metrics such as the number of visitors, bounce rate, traffic source, etc. Performance Performance cookies are used to understand and analyze the key performance indexes of the website which helps in delivering a better user experience for the visitors. Advertisement Advertisement cookies are used to provide visitors with customized advertisements based on the pages you visited previously and to analyze the effectiveness of the ad campaigns. Uncategorized Other uncategorized cookies are those that are being analyzed and have not been classified into a category as yet. Reject All Save My Preferences Accept All Products LangChain LangSmith LangGraph Methods Retrieval Agents Evaluation Resources Blog Case Studies Use Case Inspiration Experts Changelog Docs LangChain Docs LangSmith Docs Company About Careers Pricing Get a demo Sign up LangChain’s suite of products supports developers along each step of the LLM application lifecycle. Applications that can reason. Powered by LangChain. Get a demo Sign up for free From startups to global enterprises, ambitious builders choose LangChain products. Build LangChain is a framework to build with LLMs by chaining interoperable components. LangGraph is the framework for building controllable agentic workflows. Run Deploy your LLM applications at scale with LangGraph Cloud, our infrastructure purpose-built for agents. Manage Debug, collaborate, test, and monitor your LLM app in LangSmith - whether it's built with a LangChain framework or not. Build your app with LangChain Build context-aware, reasoning applications with LangChain’s flexible framework that leverages your company’s data and APIs. Future-proof your application by making vendor optionality part of your LLM infrastructure design. Learn more about LangChain Run at scale with LangGraph Cloud Deploy your LangGraph app with LangGraph Cloud for fault-tolerant scalability - including support for async background jobs, built-in persistence, and distributed task queues. Learn more about LangGraph Manage LLM performance with LangSmith Ship faster with LangSmith’s debug, test, deploy, and monitoring workflows. Don’t rely on “vibes” – add engineering rigor to your LLM-development workflow, whether you’re building with LangChain or not. Learn more about LangSmith Hear from our happy customers LangChain, LangGraph, and LangSmith help teams of all sizes, across all industries - from ambitious startups to established enterprises. “LangSmith helped us improve the accuracy and performance of Retool’s fine-tuned models. Not only did we deliver a better product by iterating with LangSmith, but we’re shipping new AI features to our users in a fraction of the time it would have taken without it.” Jamie Cuffe Head of Self-Serve and New Products “By combining the benefits of LangSmith and standing on the shoulders of a gigantic open-source community, we’re able to identify the right approaches of using LLMs in an enterprise-setting faster.” Yusuke Kaji General Manager of AI “Working with LangChain and LangSmith on the Elastic AI Assistant had a significant positive impact on the overall pace and quality of the development and shipping experience. We couldn’t have achieved  the product experience delivered to our customers without LangChain, and we couldn’t have done it at the same pace without LangSmith.” James Spiteri Director of Security Products “As soon as we heard about LangSmith, we moved our entire development stack onto it. We could have built evaluation, testing and monitoring tools in house, but with LangSmith it took us 10x less time to get a 1000x better tool.” Jose Peña Senior Manager The reference architecture enterprises adopt for success. LangChain’s suite of products can be used independently or stacked together for multiplicative impact – guiding you through building, running, and managing your LLM apps. 15M+ Monthly Downloads 100K+ Apps Powered 75K+ GitHub Stars 3K+ Contributors The biggest developer community in GenAI Learn alongside the 1M+ developers who are pushing the industry forward. Explore LangChain Get started with the LangSmith today Get a demo Sign up for free Teams building with LangChain are driving operational efficiency, increasing discovery & personalization, and delivering premium products that generate revenue. Discover Use Cases Get inspired by companies who have done it. Financial Services FinTech Technology LangSmith is the enterprise DevOps platform built for LLMs. Explore LangSmith Gain visibility to make trade offs between cost, latency, and quality. Increase developer productivity. Eliminate manual, error-prone testing. Reduce hallucinations and improve reliability. Enterprise deployment options to keep data secure. Ready to start shipping
reliable GenAI apps faster? Get started with LangChain, LangGraph, and LangSmith to enhance your LLM app development, from prototype to production. Get a demo Sign up for free Products LangChain LangSmith LangGraph Agents Evaluation Retrieval Resources Python Docs JS/TS Docs GitHub Integrations Templates Changelog LangSmith Trust Portal Company About Blog Twitter LinkedIn YouTube Community Marketing Assets Sign up for our newsletter to stay up to date Thank you! Your submission has been received! Oops! Something went wrong while submitting the form. All systems operational Privacy Policy Terms of Service
Thought:Based on the text extracted from the langchain.com website, the main headers I can see are:

- LangChain
- Products
  - LangChain
  - LangSmith
  - LangGraph
- Methods
  - Retrieval
  - Agents
  - Evaluation
- Resources
  - Blog
  - Case Studies
  - Use Case Inspiration
  - Experts
  - Changelog
- Docs
  - LangChain Docs
  - LangSmith Docs
- Company
  - About
  - Careers
  - Pricing
- Get a demo
- Sign up

The website appears to be organized around their main product offerings (LangChain, LangSmith, LangGraph) as well as resources and documentation.

Action:
\`\`\`
{
  "action": "Final Answer",
  "action_input": "The main headers on the langchain.com website are:\n\n- LangChain\n- Products\n  - LangChain\n  - LangSmith\n  - LangGraph\n- Methods\n  - Retrieval\n  - Agents\n  - Evaluation\n- Resources\n  - Blog\n  - Case Studies\n  - Use Case Inspiration\n  - Experts\n  - Changelog\n- Docs\n  - LangChain Docs\n  - LangSmith Docs\n- Company\n  - About\n  - Careers\n  - Pricing\n- Get a demo\n- Sign up"
}
\`\`\`

> Finished chain.
The main headers on the langchain.com website are:

- LangChain
- Products
  - LangChain
  - LangSmith
  - LangGraph
- Methods
  - Retrieval
  - Agents
  - Evaluation
- Resources
  - Blog
  - Case Studies
  - Use Case Inspiration
  - Experts
  - Changelog
- Docs
  - LangChain Docs
  - LangSmith Docs
- Company
  - About
  - Careers
  - Pricing
- Get a demo
- Sign up
```

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/playwright.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# MCP Toolbox for Databases

Integrate your databases with LangChain agents using MCP Toolbox.

## Overview

[MCP Toolbox for Databases](https://github.com/googleapis/genai-toolbox) is an open source MCP server for databases. It was designed with enterprise-grade and production-quality in mind. It enables you to develop tools easier, faster, and more securely by handling the complexities such as connection pooling, authentication, and more.

Toolbox Tools can be seemlessly integrated with LangChain applications. For more
information on [getting
started](https://googleapis.github.io/genai-toolbox/getting-started/local_quickstart/) or
[configuring](https://googleapis.github.io/genai-toolbox/getting-started/configure/)
MCP Toolbox, see the
[documentation](https://googleapis.github.io/genai-toolbox/getting-started/introduction/).

![architecture](https://raw.githubusercontent.com/googleapis/genai-toolbox/refs/heads/main/docs/en/getting-started/introduction/architecture.png)

## Setup

This guide assumes you have already done the following:

1. Installed [Python 3.9+](https://wiki.python.org/moin/BeginnersGuide/Download) and [pip](https://pip.pypa.io/en/stable/installation/).
2. Installed [PostgreSQL 16+ and the `psql` command-line client](https://www.postgresql.org/download/).

### 1. Setup your Database

First, let's set up a PostgreSQL database. We'll create a new database, a dedicated user for MCP Toolbox, and a `hotels` table with some sample data.

Connect to PostgreSQL using the `psql` command. You may need to adjust the command based on your PostgreSQL setup (e.g., if you need to specify a host or a different superuser).

```bash  theme={null}
psql -U postgres
```

Now, run the following SQL commands to create the user, database, and grant the necessary permissions:

```sql  theme={null}
CREATE USER toolbox_user WITH PASSWORD 'my-password';
CREATE DATABASE toolbox_db;
GRANT ALL PRIVILEGES ON DATABASE toolbox_db TO toolbox_user;
ALTER DATABASE toolbox_db OWNER TO toolbox_user;
```

Connect to your newly created database with the new user:

```sql  theme={null}
\c toolbox_db toolbox_user
```

Finally, create the `hotels` table and insert some data:

```sql  theme={null}
CREATE TABLE hotels(
  id            INTEGER NOT NULL PRIMARY KEY,
  name          VARCHAR NOT NULL,
  location      VARCHAR NOT NULL,
  price_tier    VARCHAR NOT NULL,
  booked        BIT     NOT NULL
);

INSERT INTO hotels(id, name, location, price_tier, booked)
VALUES
  (1, 'Hilton Basel', 'Basel', 'Luxury', B'0'),
  (2, 'Marriott Zurich', 'Zurich', 'Upscale', B'0'),
  (3, 'Hyatt Regency Basel', 'Basel', 'Upper Upscale', B'0');
```

You can now exit `psql` by typing `\q`.

### 2. Install MCP Toolbox

Next, we will install MCP Toolbox, define our tools in a `tools.yaml` configuration file, and run the MCP Toolbox server.

For **macOS** users, the easiest way to install is with [Homebrew](https://formulae.brew.sh/formula/mcp-toolbox):

```bash  theme={null}
brew install mcp-toolbox
```

For other platforms, [download the latest MCP Toolbox binary for your operating system and architecture.](https://github.com/googleapis/genai-toolbox/releases)

Create a `tools.yaml` file. This file defines the data sources MCP Toolbox can connect to and the tools it can expose to your agent. For production use, always use environment variables for secrets.

```yaml  theme={null}
sources:
  my-pg-source:
    kind: postgres
    host: 127.0.0.1
    port: 5432
    database: toolbox_db
    user: toolbox_user
    password: my-password

tools:
  search-hotels-by-location:
    kind: postgres-sql
    source: my-pg-source
    description: Search for hotels based on location.
    parameters:
      - name: location
        type: string
        description: The location of the hotel.
    statement: SELECT id, name, location, price_tier FROM hotels WHERE location ILIKE '%' || $1 || '%';
  book-hotel:
    kind: postgres-sql
    source: my-pg-source
    description: >-
        Book a hotel by its ID. If the hotel is successfully booked, returns a confirmation message.
    parameters:
      - name: hotel_id
        type: integer
        description: The ID of the hotel to book.
    statement: UPDATE hotels SET booked = B'1' WHERE id = $1;

toolsets:
  hotel_toolset:
    - search-hotels-by-location
    - book-hotel
```

Now, in a separate terminal window, start the MCP Toolbox server. If you installed via Homebrew, you can just run `toolbox`. If you downloaded the binary manually, you'll need to run `./toolbox` from the directory where you saved it:

```bash  theme={null}
toolbox --tools-file "tools.yaml"
```

MCP Toolbox will start on `http://127.0.0.1:5000` by default and will hot-reload if you make changes to your `tools.yaml` file.

## Instantiation

```python  theme={null}
!pip install toolbox-langchain
```

```python  theme={null}
from toolbox_langchain import ToolboxClient

with ToolboxClient("http://127.0.0.1:5000") as client:
    search_tool = await client.aload_tool("search-hotels-by-location")
```

## Invocation

```python  theme={null}
from toolbox_langchain import ToolboxClient

with ToolboxClient("http://127.0.0.1:5000") as client:
    search_tool = await client.aload_tool("search-hotels-by-location")
    results = search_tool.invoke({"location": "Basel"})
    print(results)
```

```output  theme={null}
[{"id":1,"location":"Basel","name":"Hilton Basel","price_tier":"Luxury"},{"id":3,"location":"Basel","name":"Hyatt Regency Basel","price_tier":"Upper Upscale"}]
```

## Use within an agent

Now for the fun part! We'll install the required LangChain packages and create an agent that can use the tools we defined in MCP Toolbox.

```python  theme={null}
pip install -qU toolbox-langchain langgraph langchain-google-vertexai
```

With the packages installed, we can define our agent. We will use `ChatVertexAI` for the model and `ToolboxClient` to load our tools. The [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) from `langchain.agents` creates a robust agent that can reason about which tools to call.

**Note:** Ensure your MCP Toolbox server is running in a separate terminal before executing the code below.

```python  theme={null}
from langchain.agents import create_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint.memory import MemorySaver
from toolbox_langchain import ToolboxClient


prompt = """
You're a helpful hotel assistant. You handle hotel searching and booking.
When the user searches for a hotel, list the full details for each hotel found: id, name, location, and price tier.
Always use the hotel ID for booking operations.
For any bookings, provide a clear confirmation message.
Don't ask for clarification or confirmation from the user; perform the requested action directly.
"""


async def run_queries(agent_executor):
    config = {"configurable": {"thread_id": "hotel-thread-1"}}

    # --- Query 1: Search for hotels ---
    query1 = "I need to find a hotel in Basel."
    print(f'\n--- USER: "{query1}" ---')
    inputs1 = {"messages": [("user", prompt + query1)]}
    async for event in agent_executor.astream_events(
        inputs1, config=config, version="v2"
    ):
        if event["event"] == "on_chat_model_end" and event["data"]["output"].content:
            print(f"--- AGENT: ---\n{event['data']['output'].content}")

    # --- Query 2: Book a hotel ---
    query2 = "Great, please book the Hyatt Regency Basel for me."
    print(f'\n--- USER: "{query2}" ---')
    inputs2 = {"messages": [("user", query2)]}
    async for event in agent_executor.astream_events(
        inputs2, config=config, version="v2"
    ):
        if event["event"] == "on_chat_model_end" and event["data"]["output"].content:
            print(f"--- AGENT: ---\n{event['data']['output'].content}")
```

## Run the agent

```python  theme={null}
async def main():
    await run_hotel_agent()


async def run_hotel_agent():
    model = ChatVertexAI(model_name="gemini-2.5-flash")

    # Load the tools from the running MCP Toolbox server
    async with ToolboxClient("http://127.0.0.1:5000") as client:
        tools = await client.aload_toolset("hotel_toolset")

        agent = create_agent(model, tools, checkpointer=MemorySaver())

        await run_queries(agent)


await main()
```

You've successfully connected a LangChain agent to a local database using MCP Toolbox! 🥳

***

## API reference

The primary class for this integration is `ToolboxClient`.

For more information, see the following resources:

* [Toolbox Official Documentation](https://googleapis.github.io/genai-toolbox/)
* [Toolbox GitHub Repository](https://github.com/googleapis/genai-toolbox)
* [Toolbox LangChain SDK](https://github.com/googleapis/mcp-toolbox-python-sdk/tree/main/packages/toolbox-langchain)

MCP Toolbox has a variety of features to make developing Gen AI tools for databases seamless:

* [Authenticated Parameters](https://googleapis.github.io/genai-toolbox/resources/tools/#authenticated-parameters): Bind tool inputs to values from OIDC tokens automatically, making it easy to run sensitive queries without potentially leaking data
* [Authorized Invocations](https://googleapis.github.io/genai-toolbox/resources/tools/#authorized-invocations): Restrict access to use a tool based on the users Auth token
* [OpenTelemetry](https://googleapis.github.io/genai-toolbox/how-to/export_telemetry/): Get metrics and tracing from MCP Toolbox with [OpenTelemetry](https://opentelemetry.io/docs/)

# Community and Support

We encourage you to get involved with the community:

* ⭐️ Head over to the [GitHub repository](https://github.com/googleapis/genai-toolbox) to get started and follow along with updates.
* 📚 Dive into the [official documentation](https://googleapis.github.io/genai-toolbox/getting-started/introduction/) for more advanced features and configurations.
* 💬 Join our [Discord server](https://discord.com/invite/a4XjGqtmnG) to connect with the community and ask questions.

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/toolbox.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# FireCrawl

[FireCrawl](https://firecrawl.dev/?ref=langchain) crawls and convert any website into LLM-ready data. It crawls all accessible subpages and give you clean markdown and metadata for each. No sitemap required.

FireCrawl handles complex tasks such as reverse proxies, caching, rate limits, and content blocked by JavaScript. Built by the [mendable.ai](https://mendable.ai) team.

## Overview

### Integration details

| Class                                                                                                                                                        | Package                                                                                | Local | Serializable | [JS support](https://js.langchain.com/docs/integrations/document_loaders/web_loaders/firecrawl/) |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :---: | :----------: | :----------------------------------------------------------------------------------------------: |
| [FireCrawlLoader](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.firecrawl.FireCrawlLoader.html) | [langchain-community](https://python.langchain.com/api_reference/community/index.html) |   ✅   |       ❌      |                                                 ✅                                                |

### Loader features

|      Source     | Document Lazy Loading | Native Async Support |
| :-------------: | :-------------------: | :------------------: |
| FireCrawlLoader |           ✅           |           ❌          |

## Setup

```python  theme={null}
pip install firecrawl-py
```

## Usage

You will need to get your own API key. See [firecrawl.dev](https://firecrawl.dev)

```python  theme={null}
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
```

```python  theme={null}
loader = FireCrawlLoader(
    api_key="YOUR_API_KEY", url="https://firecrawl.dev", mode="scrape"
)
```

```output  theme={null}
Document(metadata={'ogUrl': 'https://www.firecrawl.dev/', 'title': 'Home - Firecrawl', 'robots': 'follow, index', 'ogImage': 'https://www.firecrawl.dev/og.png?123', 'ogTitle': 'Firecrawl', 'sitemap': {'lastmod': '2024-08-12T00:28:16.681Z', 'changefreq': 'weekly'}, 'keywords': 'Firecrawl,Markdown,Data,Mendable,LangChain', 'sourceURL': 'https://www.firecrawl.dev/', 'ogSiteName': 'Firecrawl', 'description': 'Firecrawl crawls and converts any website into clean markdown.', 'ogDescription': 'Turn any website into LLM-ready data.', 'pageStatusCode': 200, 'ogLocaleAlternate': []}, page_content='Introducing [Smart Crawl!](https://www.firecrawl.dev/smart-crawl)\n Join the waitlist to turn any website into an API with AI\n\n\n\n[🔥 Firecrawl](/)\n\n*   [Playground](/playground)\n    \n*   [Docs](https://docs.firecrawl.dev)\n    \n*   [Pricing](/pricing)\n    \n*   [Blog](/blog)\n    \n*   Beta Features\n\n[Log In](/signin)\n[Log In](/signin)\n[Sign Up](/signin/signup)\n 8.9k\n\n[💥 Get 2 months free with yearly plan](/pricing)\n\nTurn websites into  \n_LLM-ready_ data\n=====================================\n\nPower your AI apps with clean data crawled from any website. It\'s also open-source.\n\nStart for free (500 credits)Start for free[Talk to us](https://calendly.com/d/cj83-ngq-knk/meet-firecrawl)\n\nA product by\n\n[![Mendable Logo](https://www.firecrawl.dev/images/mendable_logo_transparent.png)Mendable](https://mendable.ai)\n\n![Example Webpage](https://www.firecrawl.dev/multiple-websites.png)\n\nCrawl, Scrape, Clean\n--------------------\n\nWe crawl all accessible subpages and give you clean markdown for each. No sitemap required.\n\n    \n      [\\\n        {\\\n          "url": "https://www.firecrawl.dev/",\\\n          "markdown": "## Welcome to Firecrawl\\\n            Firecrawl is a web scraper that allows you to extract the content of a webpage."\\\n        },\\\n        {\\\n          "url": "https://www.firecrawl.dev/features",\\\n          "markdown": "## Features\\\n            Discover how Firecrawl\'s cutting-edge features can \\\n            transform your data operations."\\\n        },\\\n        {\\\n          "url": "https://www.firecrawl.dev/pricing",\\\n          "markdown": "## Pricing Plans\\\n            Choose the perfect plan that fits your needs."\\\n        },\\\n        {\\\n          "url": "https://www.firecrawl.dev/about",\\\n          "markdown": "## About Us\\\n            Learn more about Firecrawl\'s mission and the \\\n            team behind our innovative platform."\\\n        }\\\n      ]\n      \n\nNote: The markdown has been edited for display purposes.\n\nTrusted by Top Companies\n------------------------\n\n[![Customer Logo](https://www.firecrawl.dev/logos/zapier.png)](https://www.zapier.com)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/gamma.svg)](https://gamma.app)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/nvidia-com.png)](https://www.nvidia.com)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/teller-io.svg)](https://www.teller.io)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/stackai.svg)](https://www.stack-ai.com)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/palladiumdigital-co-uk.svg)](https://www.palladiumdigital.co.uk)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/worldwide-casting-com.svg)](https://www.worldwide-casting.com)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/open-gov-sg.png)](https://www.open.gov.sg)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/bain-com.svg)](https://www.bain.com)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/demand-io.svg)](https://www.demand.io)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/nocodegarden-io.png)](https://www.nocodegarden.io)\n\n[![Customer Logo](https://www.firecrawl.dev/logos/cyberagent-co-jp.svg)](https://www.cyberagent.co.jp)\n\nIntegrate today\n---------------\n\nEnhance your applications with top-tier web scraping and crawling capabilities.\n\n#### Scrape\n\nExtract markdown or structured data from websites quickly and efficiently.\n\n#### Crawling\n\nNavigate and retrieve data from all accessible subpages, even without a sitemap.\n\nNode.js\n\nPython\n\ncURL\n\n1\n\n2\n\n3\n\n4\n\n5\n\n6\n\n7\n\n8\n\n9\n\n10\n\n// npm install @mendable/firecrawl-js  \n  \nimport FirecrawlApp from \'@mendable/firecrawl-js\';  \n  \nconst app \\= new FirecrawlApp({ apiKey: "fc-YOUR\\_API\\_KEY" });  \n  \n// Scrape a website:  \nconst scrapeResult \\= await app.scrapeUrl(\'firecrawl.dev\');  \n  \nconsole.log(scrapeResult.data.markdown)\n\n#### Use well-known tools\n\nAlready fully integrated with the greatest existing tools and workflows.\n\n[![LlamaIndex](https://www.firecrawl.dev/logos/llamaindex.svg)](https://docs.llamaindex.ai/en/stable/examples/data_connectors/WebPageDemo/#using-firecrawl-reader/)\n[![LangChain](https://www.firecrawl.dev/integrations/langchain.png)](https://python.langchain.com/docs/integrations/document_loaders/firecrawl/)\n[![Dify](https://www.firecrawl.dev/logos/dify.png)](https://dify.ai/blog/dify-ai-blog-integrated-with-firecrawl/)\n[![Dify](https://www.firecrawl.dev/integrations/langflow_2.png)](https://www.langflow.org/)\n[![Flowise](https://www.firecrawl.dev/integrations/flowise.png)](https://flowiseai.com/)\n[![CrewAI](https://www.firecrawl.dev/integrations/crewai.png)](https://crewai.com/)\n\n#### Start for free, scale easily\n\nKick off your journey for free and scale seamlessly as your project expands.\n\n[Try it out](/signin/signup)\n\n#### Open-source\n\nDeveloped transparently and collaboratively. Join our community of contributors.\n\n[Check out our repo](https://github.com/mendableai/firecrawl)\n\nWe handle the hard stuff\n------------------------\n\nRotating proxies, caching, rate limits, js-blocked content and more\n\n#### Crawling\n\nFirecrawl crawls all accessible subpages, even without a sitemap.\n\n#### Dynamic content\n\nFirecrawl gathers data even if a website uses javascript to render content.\n\n#### To Markdown\n\nFirecrawl returns clean, well formatted markdown - ready for use in LLM applications\n\n#### Crawling Orchestration\n\nFirecrawl orchestrates the crawling process in parallel for the fastest results.\n\n#### Caching\n\nFirecrawl caches content, so you don\'t have to wait for a full scrape unless new content exists.\n\n#### Built for AI\n\nBuilt by LLM engineers, for LLM engineers. Giving you clean data the way you want it.\n\nOur wall of love\n\nDon\'t take our word for it\n--------------------------\n\n![Greg Kamradt](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-02.0afeb750.jpg&w=96&q=75)\n\nGreg Kamradt\n\n[@GregKamradt](https://twitter.com/GregKamradt/status/1780300642197840307)\n\nLLM structured data via API, handling requests, cleaning, and crawling. Enjoyed the early preview.\n\n![Amit Naik](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-03.ff5dbe11.jpg&w=96&q=75)\n\nAmit Naik\n\n[@suprgeek](https://twitter.com/suprgeek/status/1780338213351035254)\n\n#llm success with RAG relies on Retrieval. Firecrawl by @mendableai structures web content for processing. 👏\n\n![Jerry Liu](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-04.76bef0df.jpg&w=96&q=75)\n\nJerry Liu\n\n[@jerryjliu0](https://twitter.com/jerryjliu0/status/1781122933349572772)\n\nFirecrawl is awesome 🔥 Turns web pages into structured markdown for LLM apps, thanks to @mendableai.\n\n![Bardia Pourvakil](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-01.025350bc.jpeg&w=96&q=75)\n\nBardia Pourvakil\n\n[@thepericulum](https://twitter.com/thepericulum/status/1781397799487078874)\n\nThese guys ship. I wanted types for their node SDK, and less than an hour later, I got them. Can\'t recommend them enough.\n\n![latentsauce 🧘🏽](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-07.c2285d35.jpeg&w=96&q=75)\n\nlatentsauce 🧘🏽\n\n[@latentsauce](https://twitter.com/latentsauce/status/1781738253927735331)\n\nFirecrawl simplifies data preparation significantly, exactly what I was hoping for. Thank you for creating Firecrawl ❤️❤️❤️\n\n![Greg Kamradt](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-02.0afeb750.jpg&w=96&q=75)\n\nGreg Kamradt\n\n[@GregKamradt](https://twitter.com/GregKamradt/status/1780300642197840307)\n\nLLM structured data via API, handling requests, cleaning, and crawling. Enjoyed the early preview.\n\n![Amit Naik](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-03.ff5dbe11.jpg&w=96&q=75)\n\nAmit Naik\n\n[@suprgeek](https://twitter.com/suprgeek/status/1780338213351035254)\n\n#llm success with RAG relies on Retrieval. Firecrawl by @mendableai structures web content for processing. 👏\n\n![Jerry Liu](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-04.76bef0df.jpg&w=96&q=75)\n\nJerry Liu\n\n[@jerryjliu0](https://twitter.com/jerryjliu0/status/1781122933349572772)\n\nFirecrawl is awesome 🔥 Turns web pages into structured markdown for LLM apps, thanks to @mendableai.\n\n![Bardia Pourvakil](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-01.025350bc.jpeg&w=96&q=75)\n\nBardia Pourvakil\n\n[@thepericulum](https://twitter.com/thepericulum/status/1781397799487078874)\n\nThese guys ship. I wanted types for their node SDK, and less than an hour later, I got them. Can\'t recommend them enough.\n\n![latentsauce 🧘🏽](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-07.c2285d35.jpeg&w=96&q=75)\n\nlatentsauce 🧘🏽\n\n[@latentsauce](https://twitter.com/latentsauce/status/1781738253927735331)\n\nFirecrawl simplifies data preparation significantly, exactly what I was hoping for. Thank you for creating Firecrawl ❤️❤️❤️\n\n![Michael Ning](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-05.76d7cd3e.png&w=96&q=75)\n\nMichael Ning\n\n[](#)\n\nFirecrawl is impressive, saving us 2/3 the tokens and allowing gpt3.5turbo use over gpt4. Major savings in time and money.\n\n![Alex Reibman 🖇️](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-06.4ee7cf5a.jpeg&w=96&q=75)\n\nAlex Reibman 🖇️\n\n[@AlexReibman](https://twitter.com/AlexReibman/status/1780299595484131836)\n\nMoved our internal agent\'s web scraping tool from Apify to Firecrawl because it benchmarked 50x faster with AgentOps.\n\n![Michael](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-08.0bed40be.jpeg&w=96&q=75)\n\nMichael\n\n[@michael\\_chomsky](#)\n\nI really like some of the design decisions Firecrawl made, so I really want to share with others.\n\n![Paul Scott](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-09.d303b5b4.png&w=96&q=75)\n\nPaul Scott\n\n[@palebluepaul](https://twitter.com/palebluepaul)\n\nAppreciating your lean approach, Firecrawl ticks off everything on our list without the cost prohibitive overkill.\n\n![Michael Ning](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-05.76d7cd3e.png&w=96&q=75)\n\nMichael Ning\n\n[](#)\n\nFirecrawl is impressive, saving us 2/3 the tokens and allowing gpt3.5turbo use over gpt4. Major savings in time and money.\n\n![Alex Reibman 🖇️](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-06.4ee7cf5a.jpeg&w=96&q=75)\n\nAlex Reibman 🖇️\n\n[@AlexReibman](https://twitter.com/AlexReibman/status/1780299595484131836)\n\nMoved our internal agent\'s web scraping tool from Apify to Firecrawl because it benchmarked 50x faster with AgentOps.\n\n![Michael](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-08.0bed40be.jpeg&w=96&q=75)\n\nMichael\n\n[@michael\\_chomsky](#)\n\nI really like some of the design decisions Firecrawl made, so I really want to share with others.\n\n![Paul Scott](https://www.firecrawl.dev/_next/image?url=%2F_next%2Fstatic%2Fmedia%2Ftestimonial-09.d303b5b4.png&w=96&q=75)\n\nPaul Scott\n\n[@palebluepaul](https://twitter.com/palebluepaul)\n\nAppreciating your lean approach, Firecrawl ticks off everything on our list without the cost prohibitive overkill.\n\nFlexible Pricing\n----------------\n\nStart for free, then scale as you grow\n\nYearly (17% off)Yearly (2 months free)Monthly\n\nFree Plan\n---------\n\n500 credits\n\n$0/month\n\n*   Scrape 500 pages\n*   5 /scrape per min\n*   1 /crawl per min\n\nGet Started\n\nHobby\n-----\n\n3,000 credits\n\n$16/month\n\n*   Scrape 3,000 pages\n*   10 /scrape per min\n*   3 /crawl per min\n\nSubscribe\n\nStandardMost Popular\n--------------------\n\n100,000 credits\n\n$83/month\n\n*   Scrape 100,000 pages\n*   50 /scrape per min\n*   10 /crawl per min\n\nSubscribe\n\nGrowth\n------\n\n500,000 credits\n\n$333/month\n\n*   Scrape 500,000 pages\n*   500 /scrape per min\n*   50 /crawl per min\n*   Priority Support\n\nSubscribe\n\nEnterprise Plan\n---------------\n\nUnlimited credits. Custom RPMs.\n\nTalk to us\n\n*   Top priority support\n*   Feature Acceleration\n*   SLAs\n*   Account Manager\n*   Custom rate limits volume\n*   Custom concurrency limits\n*   Beta features access\n*   CEO\'s number\n\n\\* a /scrape refers to the [scrape](https://docs.firecrawl.dev/api-reference/endpoint/scrape)\n API endpoint.\n\n\\* a /crawl refers to the [crawl](https://docs.firecrawl.dev/api-reference/endpoint/crawl)\n API endpoint.\n\nScrape Credits\n--------------\n\nScrape credits are consumed for each API request, varying by endpoint and feature.\n\n| Features | Credits per page |\n| --- | --- |\n| Scrape(/scrape) | 1   |\n| Crawl(/crawl) | 1   |\n| Search(/search) | 1   |\n| Scrape + LLM extraction (/scrape) | 50  |\n\n[🔥](/)\n\nReady to _Build?_\n-----------------\n\nStart scraping web data for your AI apps today.  \nNo credit card needed.\n\n[Get Started](/signin)\n\n[Talk to us](https://calendly.com/d/cj83-ngq-knk/meet-firecrawl)\n\nFAQ\n---\n\nFrequently asked questions about Firecrawl\n\n#### General\n\nWhat is Firecrawl?\n\nFirecrawl turns entire websites into clean, LLM-ready markdown or structured data. Scrape, crawl and extract the web with a single API. Ideal for AI companies looking to empower their LLM applications with web data.\n\nWhat sites work?\n\nFirecrawl is best suited for business websites, docs and help centers. We currently don\'t support social media platforms.\n\nWho can benefit from using Firecrawl?\n\nFirecrawl is tailored for LLM engineers, data scientists, AI researchers, and developers looking to harness web data for training machine learning models, market research, content aggregation, and more. It simplifies the data preparation process, allowing professionals to focus on insights and model development.\n\nIs Firecrawl open-source?\n\nYes, it is. You can check out the repository on GitHub. Keep in mind that this repository is currently in its early stages of development. We are in the process of merging custom modules into this mono repository.\n\n#### Scraping & Crawling\n\nHow does Firecrawl handle dynamic content on websites?\n\nUnlike traditional web scrapers, Firecrawl is equipped to handle dynamic content rendered with JavaScript. It ensures comprehensive data collection from all accessible subpages, making it a reliable tool for scraping websites that rely heavily on JS for content delivery.\n\nWhy is it not crawling all the pages?\n\nThere are a few reasons why Firecrawl may not be able to crawl all the pages of a website. Some common reasons include rate limiting, and anti-scraping mechanisms, disallowing the crawler from accessing certain pages. If you\'re experiencing issues with the crawler, please reach out to our support team at hello@firecrawl.com.\n\nCan Firecrawl crawl websites without a sitemap?\n\nYes, Firecrawl can access and crawl all accessible subpages of a website, even in the absence of a sitemap. This feature enables users to gather data from a wide array of web sources with minimal setup.\n\nWhat formats can Firecrawl convert web data into?\n\nFirecrawl specializes in converting web data into clean, well-formatted markdown. This format is particularly suited for LLM applications, offering a structured yet flexible way to represent web content.\n\nHow does Firecrawl ensure the cleanliness of the data?\n\nFirecrawl employs advanced algorithms to clean and structure the scraped data, removing unnecessary elements and formatting the content into readable markdown. This process ensures that the data is ready for use in LLM applications without further preprocessing.\n\nIs Firecrawl suitable for large-scale data scraping projects?\n\nAbsolutely. Firecrawl offers various pricing plans, including a Scale plan that supports scraping of millions of pages. With features like caching and scheduled syncs, it\'s designed to efficiently handle large-scale data scraping and continuous updates, making it ideal for enterprises and large projects.\n\nDoes it respect robots.txt?\n\nYes, Firecrawl crawler respects the rules set in a website\'s robots.txt file. If you notice any issues with the way Firecrawl interacts with your website, you can adjust the robots.txt file to control the crawler\'s behavior. Firecrawl user agent name is \'FirecrawlAgent\'. If you notice any behavior that is not expected, please let us know at hello@firecrawl.com.\n\nWhat measures does Firecrawl take to handle web scraping challenges like rate limits and caching?\n\nFirecrawl is built to navigate common web scraping challenges, including reverse proxies, rate limits, and caching. It smartly manages requests and employs caching techniques to minimize bandwidth usage and avoid triggering anti-scraping mechanisms, ensuring reliable data collection.\n\nDoes Firecrawl handle captcha or authentication?\n\nFirecrawl avoids captcha by using stealth proxyies. When it encounters captcha, it attempts to solve it automatically, but this is not always possible. We are working to add support for more captcha solving methods. Firecrawl can handle authentication by providing auth headers to the API.\n\n#### API Related\n\nWhere can I find my API key?\n\nClick on the dashboard button on the top navigation menu when logged in and you will find your API key in the main screen and under API Keys.\n\n#### Billing\n\nIs Firecrawl free?\n\nFirecrawl is free for the first 500 scraped pages (500 free credits). After that, you can upgrade to our Standard or Scale plans for more credits.\n\nIs there a pay per use plan instead of monthly?\n\nNo we do not currently offer a pay per use plan, instead you can upgrade to our Standard or Growth plans for more credits and higher rate limits.\n\nHow many credit does scraping, crawling, and extraction cost?\n\nScraping costs 1 credit per page. Crawling costs 1 credit per page.\n\nDo you charge for failed requests (scrape, crawl, extract)?\n\nWe do not charge for any failed requests (scrape, crawl, extract). Please contact support at help@firecrawl.dev if you have any questions.\n\nWhat payment methods do you accept?\n\nWe accept payments through Stripe which accepts most major credit cards, debit cards, and PayPal.\n\n[🔥](/)\n\n© A product by Mendable.ai - All rights reserved.\n\n[StatusStatus](https://firecrawl.betteruptime.com)\n[Terms of ServiceTerms of Service](/terms-of-service)\n[Privacy PolicyPrivacy Policy](/privacy-policy)\n\n[Twitter](https://twitter.com/mendableai)\n[GitHub](https://github.com/mendableai)\n[Discord](https://discord.gg/gSmWdAkdwd)\n\n###### Helpful Links\n\n*   [Status](https://firecrawl.betteruptime.com/)\n    \n*   [Pricing](/pricing)\n    \n*   [Blog](https://www.firecrawl.dev/blog)\n    \n*   [Docs](https://docs.firecrawl.dev)\n    \n\nBacked by![Y Combinator Logo](https://www.firecrawl.dev/images/yc.svg)\n\n![SOC 2 Type II](https://www.firecrawl.dev/soc2type2badge.png)\n\n###### Resources\n\n*   [Community](#0)\n    \n*   [Terms of service](#0)\n    \n*   [Collaboration features](#0)\n    \n\n###### Legals\n\n*   [Refund policy](#0)\n    \n*   [Terms & Conditions](#0)\n    \n*   [Privacy policy](#0)\n    \n*   [Brand Kit](#0)')
```

```python  theme={null}
pages = []
for doc in loader.lazy_load():
    pages.append(doc)
    if len(pages) >= 10:
        # do some paged operation, e.g.
        # index.upsert(page)

        pages = []
```

```python  theme={null}
pages
```

## Modes

* `scrape`: Scrape single url and return the markdown.
* `crawl`: Crawl the url and all accessible sub pages and return the markdown for each one.
* `map`: Maps the URL and returns a list of semantically related pages.

### Crawl

```python  theme={null}
loader = FireCrawlLoader(
    api_key="YOUR_API_KEY",
    url="https://firecrawl.dev",
    mode="crawl",
)
```

```python  theme={null}
data = loader.load()
```

```python  theme={null}
print(pages[0].page_content[:100])
print(pages[0].metadata)
```

#### Crawl Options

You can also pass `params` to the loader. This is a dictionary of options to pass to the crawler. See the [FireCrawl API documentation](https://github.com/mendableai/firecrawl-py) for more information.

### Map

```python  theme={null}
loader = FireCrawlLoader(api_key="YOUR_API_KEY", url="firecrawl.dev", mode="map")
```

```python  theme={null}
docs = loader.load()
```

```python  theme={null}
docs
```

#### Map Options

You can also pass `params` to the loader. This is a dictionary of options to pass to the loader. See the [FireCrawl API documentation](https://github.com/mendableai/firecrawl-py) for more information.

***

## API reference

For detailed documentation of all `FireCrawlLoader` features and configurations head to the API reference: [python.langchain.com/api\_reference/community/document\_loaders/langchain\_community.document\_loaders.firecrawl.FireCrawlLoader.html](https://python.langchain.com/api_reference/community/document_loaders/langchain_community.document_loaders.firecrawl.FireCrawlLoader.html)

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/document_loaders/firecrawl.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>


# ArXiv

This notebook goes over how to use the `arxiv` tool with an agent.

First, you need to install the `arxiv` python package.

```python  theme={null}
pip install -qU  langchain-community arxiv
```

```python  theme={null}
from langchain_classic import hub
from langchain.agents import AgentExecutor, create_agent, load_tools
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(temperature=0.0)
tools = load_tools(
    ["arxiv"],
)
prompt = hub.pull("hwchase17/react")

agent = create_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

```python  theme={null}
agent_executor.invoke(
    {
        "input": "What's the paper 1605.08386 about?",
    }
)
```

```output  theme={null}
> Entering new AgentExecutor chain...
I should use the arxiv tool to search for the paper with the given identifier.
Action: arxiv
Action Input: 1605.08386Published: 2016-05-26
Title: Heat-bath random walks with Markov bases
Authors: Caprice Stanley, Tobias Windisch
Summary: Graphs on lattice points are studied whose edges come from a finite set of
allowed moves of arbitrary length. We show that the diameter of these graphs on
fibers of a fixed integer matrix can be bounded from above by a constant. We
then study the mixing behaviour of heat-bath random walks on these graphs. We
also state explicit conditions on the set of moves so that the heat-bath random
walk, a generalization of the Glauber dynamics, is an expander in fixed
dimension.The paper "1605.08386" is titled "Heat-bath random walks with Markov bases" and is authored by Caprice Stanley and Tobias Windisch. It was published on May 26, 2016. The paper discusses the study of graphs on lattice points with edges coming from a finite set of allowed moves. It explores the diameter of these graphs and the mixing behavior of heat-bath random walks on them. The paper also discusses conditions for the heat-bath random walk to be an expander in fixed dimension.
Final Answer: The paper "1605.08386" is about heat-bath random walks with Markov bases.

> Finished chain.
```

```output  theme={null}
{'input': "What's the paper 1605.08386 about?",
 'output': 'The paper "1605.08386" is about heat-bath random walks with Markov bases.'}
```

## The ArXiv API Wrapper

The tool uses the `API Wrapper`. Below, we explore some of the features it provides.

```python  theme={null}
from langchain_community.utilities import ArxivAPIWrapper
```

You can use the ArxivAPIWrapper to get information about a scientific article or articles. The query text is limited to 300 characters.

The ArxivAPIWrapper returns these article fields:

* Publishing date
* Title
* Authors
* Summary

The following query returns information about one article with the arxiv ID "1605.08386".

```python  theme={null}
arxiv = ArxivAPIWrapper()
docs = arxiv.run("1605.08386")
docs
```

```output  theme={null}
'Published: 2016-05-26\nTitle: Heat-bath random walks with Markov bases\nAuthors: Caprice Stanley, Tobias Windisch\nSummary: Graphs on lattice points are studied whose edges come from a finite set of\nallowed moves of arbitrary length. We show that the diameter of these graphs on\nfibers of a fixed integer matrix can be bounded from above by a constant. We\nthen study the mixing behaviour of heat-bath random walks on these graphs. We\nalso state explicit conditions on the set of moves so that the heat-bath random\nwalk, a generalization of the Glauber dynamics, is an expander in fixed\ndimension.'
```

Now, we want to get information about one author, `Caprice Stanley`.

This query returns information about three articles. By default, the query returns information only about three top articles.

```python  theme={null}
docs = arxiv.run("Caprice Stanley")
docs
```

```output  theme={null}
'Published: 2017-10-10\nTitle: On Mixing Behavior of a Family of Random Walks Determined by a Linear Recurrence\nAuthors: Caprice Stanley, Seth Sullivant\nSummary: We study random walks on the integers mod $G_n$ that are determined by an\ninteger sequence $\\{ G_n \\}_{n \\geq 1}$ generated by a linear recurrence\nrelation. Fourier analysis provides explicit formulas to compute the\neigenvalues of the transition matrices and we use this to bound the mixing time\nof the random walks.\n\nPublished: 2016-05-26\nTitle: Heat-bath random walks with Markov bases\nAuthors: Caprice Stanley, Tobias Windisch\nSummary: Graphs on lattice points are studied whose edges come from a finite set of\nallowed moves of arbitrary length. We show that the diameter of these graphs on\nfibers of a fixed integer matrix can be bounded from above by a constant. We\nthen study the mixing behaviour of heat-bath random walks on these graphs. We\nalso state explicit conditions on the set of moves so that the heat-bath random\nwalk, a generalization of the Glauber dynamics, is an expander in fixed\ndimension.\n\nPublished: 2003-03-18\nTitle: Calculation of fluxes of charged particles and neutrinos from atmospheric showers\nAuthors: V. Plyaskin\nSummary: The results on the fluxes of charged particles and neutrinos from a\n3-dimensional (3D) simulation of atmospheric showers are presented. An\nagreement of calculated fluxes with data on charged particles from the AMS and\nCAPRICE detectors is demonstrated. Predictions on neutrino fluxes at different\nexperimental sites are compared with results from other calculations.'
```

Now, we are trying to find information about non-existing article. In this case, the response is "No good Arxiv Result was found"

```python  theme={null}
docs = arxiv.run("1605.08386WWW")
docs
```

```output  theme={null}
'No good Arxiv Result was found'
```

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/tools/arxiv.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>
