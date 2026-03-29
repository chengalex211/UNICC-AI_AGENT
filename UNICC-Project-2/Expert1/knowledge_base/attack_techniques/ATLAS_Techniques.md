# ATLAS Attack Techniques
**Source:** MITRE ATLAS (Adversarial Threat Landscape for AI Systems)
**Filtered:** LLM / AI Agent relevant tactics only
**Count:** 61 techniques

---

## AML.T0000 — Search Open Technical Databases

**Tactics:** AML.TA0002  
**Attack Layer:** social_engineering  
**ID:** `AML.T0000`  

Adversaries may search for publicly available research and technical documentation to learn how and where AI is used within a victim organization.
The adversary can use this information to identify targets for attack, or to tailor an existing attack to make it more effective.
Organizations often use open source model architectures trained on additional proprietary data in production.
Knowledge of this underlying architecture allows the adversary to craft more realistic proxy models ([Create Proxy AI Model](/techniques/AML.T0005)).
An adversary can search these resources for publications for authors employed at the victim organization.

Research and technical materials may exist as academic papers published in [Journals and Conference Proceedings](/techniques/AML.T0000.000), or stored in [Pre-Print Repositories](/techniques/AML.T0000.001), as well as [Technical Blogs](/techniques/AML.T0000.002).

---

## AML.T0001 — Search Open AI Vulnerability Analysis

**Tactics:** AML.TA0002  
**Attack Layer:** model  
**ID:** `AML.T0001`  

Much like the [Search Open Technical Databases](/techniques/AML.T0000), there is often ample research available on the vulnerabilities of common AI models. Once a target has been identified, an adversary will likely try to identify any pre-existing work that has been done for this class of models.
This will include not only reading academic papers that may identify the particulars of a successful attack, but also identifying pre-existing implementations of those attacks. The adversary may obtain [Adversarial AI Attack Implementations](/techniques/AML.T0016.000) or develop their own [Adversarial AI Attacks](/techniques/AML.T0017.000) if necessary.

---

## AML.T0003 — Search Victim-Owned Websites

**Tactics:** AML.TA0002  
**Attack Layer:** social_engineering  
**ID:** `AML.T0003`  

Adversaries may search websites owned by the victim for information that can be used during targeting.
Victim-owned websites may contain technical details about their AI-enabled products or services.
Victim-owned websites may contain a variety of details, including names of departments/divisions, physical locations, and data about key employees such as names, roles, and contact info.
These sites may also have details highlighting business operations and relationships.

Adversaries may search victim-owned websites to gather actionable information.
This information may help adversaries tailor their attacks (e.g. [Adversarial AI Attacks](/techniques/AML.T0017.000) or [Manual Modification](/techniques/AML.T0043.003)).
Information from these sources may reveal opportunities for other forms of reconnaissance (e.g. [Search Open Technical Databases](/techniques/AML.T0000) or [Search Open AI Vulnerability Analysis](/techniques/AML.T0001))

---

## AML.T0004 — Search Application Repositories

**Tactics:** AML.TA0002  
**Attack Layer:** social_engineering  
**ID:** `AML.T0004`  

Adversaries may search open application repositories during targeting.
Examples of these include Google Play, the iOS App store, the macOS App Store, and the Microsoft Store.

Adversaries may craft search queries seeking applications that contain AI-enabled components.
Frequently, the next step is to [Acquire Public AI Artifacts](/techniques/AML.T0002).

---

## AML.T0006 — Active Scanning

**Tactics:** AML.TA0002  
**Attack Layer:** model  
**ID:** `AML.T0006`  

An adversary may probe or scan the victim system to gather information for targeting. This is distinct from other reconnaissance techniques that do not involve direct interaction with the victim system.

Adversaries may scan for open ports on a potential victim's network, which can indicate specific services or tools the victim is utilizing. This could include a scan for tools related to AI DevOps or AI services themselves such as public AI chat agents (ex: [Copilot Studio Hunter](https://github.com/mbrg/power-pwn/wiki/Modules:-Copilot-Studio-Hunter-%E2%80%90-Enum)). They can also send emails to organization service addresses and inspect the replies for indicators that an AI agent is managing the inbox.

Information gained from Active Scanning may yield targets that provide opportunities for other forms of reconnaissance such as [Search Open Technical Databases](/techniques/AML.T0000), [Search Open AI Vulnerability Analysis](/techniques/AML.T0001), or [Gather RAG-Indexed Targets](/techniques/AML.T0064).

---

## AML.T0010 — AI Supply Chain Compromise

**Tactics:** AML.TA0004  
**Attack Layer:** social_engineering  
**ID:** `AML.T0010`  

Adversaries may gain initial access to a system by compromising the unique portions of the AI supply chain.
This could include [Hardware](/techniques/AML.T0010.000), [Data](/techniques/AML.T0010.002) and its annotations, parts of the AI [AI Software](/techniques/AML.T0010.001) stack, or the [Model](/techniques/AML.T0010.003) itself.
In some instances the attacker will need secondary access to fully carry out an attack using compromised components of the supply chain.

---

## AML.T0040 — AI Model Inference API Access

**Tactics:** AML.TA0000  
**Attack Layer:** model  
**ID:** `AML.T0040`  

Adversaries may gain access to a model via legitimate access to the inference API.
Inference API access can be a source of information to the adversary ([Discover AI Model Ontology](/techniques/AML.T0013), [Discover AI Model Family](/techniques/AML.T0014)), a means of staging the attack ([Verify Attack](/techniques/AML.T0042), [Craft Adversarial Data](/techniques/AML.T0043)), or for introducing data to the target system for Impact ([Evade AI Model](/techniques/AML.T0015), [Erode AI Model Integrity](/techniques/AML.T0031)).

Many systems rely on the same models provided via an inference API, which means they share the same vulnerabilities. This is especially true of foundation models which are prohibitively resource intensive to train. Adversaries may use their access to model APIs to identify vulnerabilities such as jailbreaks or hallucinations and then target applications that use the same models.

---

## AML.T0047 — AI-Enabled Product or Service

**Tactics:** AML.TA0000  
**Attack Layer:** social_engineering  
**ID:** `AML.T0047`  

Adversaries may use a product or service that uses artificial intelligence under the hood to gain access to the underlying AI model.
This type of indirect model access may reveal details of the AI model or its inferences in logs or metadata.

---

## AML.T0041 — Physical Environment Access

**Tactics:** AML.TA0000  
**Attack Layer:** social_engineering  
**ID:** `AML.T0041`  

In addition to the attacks that take place purely in the digital domain, adversaries may also exploit the physical environment for their attacks.
If the model is interacting with data collected from the real world in some way, the adversary can influence the model through access to wherever the data is being collected.
By modifying the data in the collection process, the adversary can perform modified versions of attacks designed for digital access.

---

## AML.T0044 — Full AI Model Access

**Tactics:** AML.TA0000  
**Attack Layer:** model  
**ID:** `AML.T0044`  

Adversaries may gain full "white-box" access to an AI model.
This means the adversary has complete knowledge of the model architecture, its parameters, and class ontology.
They may exfiltrate the model to [Craft Adversarial Data](/techniques/AML.T0043) and [Verify Attack](/techniques/AML.T0042) in an offline where it is hard to detect their behavior.

---

## AML.T0013 — Discover AI Model Ontology

**Tactics:** AML.TA0008  
**Attack Layer:** model  
**ID:** `AML.T0013`  

Adversaries may discover the ontology of an AI model's output space, for example, the types of objects a model can detect.
The adversary may discovery the ontology by repeated queries to the model, forcing it to enumerate its output space.
Or the ontology may be discovered in a configuration file or in documentation about the model.

The model ontology helps the adversary understand how the model is being used by the victim.
It is useful to the adversary in creating targeted attacks.

---

## AML.T0014 — Discover AI Model Family

**Tactics:** AML.TA0008  
**Attack Layer:** model  
**ID:** `AML.T0014`  

Adversaries may discover the general family of model.
General information about the model may be revealed in documentation, or the adversary may use carefully constructed examples and analyze the model's responses to categorize it.

Knowledge of the model family can help the adversary identify means of attacking the model and help tailor the attack.

---

## AML.T0020 — Poison Training Data

**Tactics:** AML.TA0003, AML.TA0006  
**Attack Layer:** model  
**ID:** `AML.T0020`  

Adversaries may attempt to poison datasets used by an AI model by modifying the underlying data or its labels.
This allows the adversary to embed vulnerabilities in AI models trained on the data that may not be easily detectable.
Data poisoning attacks may or may not require modifying the labels.
The embedded vulnerability is activated at a later time by data samples with an [Insert Backdoor Trigger](/techniques/AML.T0043.004)

Poisoned data can be introduced via [AI Supply Chain Compromise](/techniques/AML.T0010) or the data may be poisoned after the adversary gains [Initial Access](/tactics/AML.TA0004) to the system.

---

## AML.T0005 — Create Proxy AI Model

**Tactics:** AML.TA0001  
**Attack Layer:** model  
**ID:** `AML.T0005`  

Adversaries may obtain models to serve as proxies for the target model in use at the victim organization.
Proxy models are used to simulate complete access to the target model in a fully offline manner.

Adversaries may train models from representative datasets, attempt to replicate models from victim inference APIs, or use available pre-trained models.

---

## AML.T0007 — Discover AI Artifacts

**Tactics:** AML.TA0008  
**Attack Layer:** social_engineering  
**ID:** `AML.T0007`  

Adversaries may search private sources to identify AI learning artifacts that exist on the system and gather information about them.
These artifacts can include the software stack used to train and deploy models, training and testing data management systems, container registries, software repositories, and model zoos.

This information can be used to identify targets for further collection, exfiltration, or disruption, and to tailor and improve attacks.

---

## AML.T0011 — User Execution

**Tactics:** AML.TA0005  
**Attack Layer:** social_engineering  
**ID:** `AML.T0011`  

An adversary may rely upon specific actions by a user in order to gain execution.
Users may inadvertently execute unsafe code introduced via [AI Supply Chain Compromise](/techniques/AML.T0010).
Users may be subjected to social engineering to get them to execute malicious code by, for example, opening a malicious document file or link.

---

## AML.T0012 — Valid Accounts

**Tactics:** AML.TA0004, AML.TA0012  
**Attack Layer:** social_engineering  
**ID:** `AML.T0012`  

Adversaries may obtain and abuse credentials of existing accounts as a means of gaining Initial Access.
Credentials may take the form of usernames and passwords of individual user accounts or API keys that provide access to various AI resources and services.

Compromised credentials may provide access to additional AI artifacts and allow the adversary to perform [Discover AI Artifacts](/techniques/AML.T0007).
Compromised credentials may also grant an adversary increased privileges such as write access to AI artifacts used during development or production.

---

## AML.T0015 — Evade AI Model

**Tactics:** AML.TA0004, AML.TA0007, AML.TA0011  
**Attack Layer:** model  
**ID:** `AML.T0015`  

Adversaries can [Craft Adversarial Data](/techniques/AML.T0043) that prevents an AI model from correctly identifying the contents of the data or [Generate Deepfakes](/techniques/AML.T0088) that fools an AI model expecting authentic data.

This technique can be used to evade a downstream task where AI is utilized. The adversary may evade AI-based virus/malware detection or network scanning towards the goal of a traditional cyber attack. AI model evasion through deepfake generation may also provide initial access to systems that use AI-based biometric authentication.

---

## AML.T0018 — Manipulate AI Model

**Tactics:** AML.TA0006, AML.TA0001  
**Attack Layer:** model  
**ID:** `AML.T0018`  

Adversaries may directly manipulate an AI model to change its behavior or introduce malicious code. Manipulating a model gives the adversary a persistent change in the system. This can include poisoning the model by changing its weights, modifying the model architecture to change its behavior, and embedding malware which may be executed when the model is loaded.

---

## AML.T0035 — AI Artifact Collection

**Tactics:** AML.TA0009  
**Attack Layer:** social_engineering  
**ID:** `AML.T0035`  

Adversaries may collect AI artifacts for [Exfiltration](/tactics/AML.TA0010) or for use in [AI Attack Staging](/tactics/AML.TA0001).
AI artifacts include models and datasets as well as other telemetry data produced when interacting with a model.

---

## AML.T0036 — Data from Information Repositories

**Tactics:** AML.TA0009  
**Attack Layer:** social_engineering  
**ID:** `AML.T0036`  

Adversaries may leverage information repositories to mine valuable information.
Information repositories are tools that allow for storage of information, typically to facilitate collaboration or information sharing between users, and can store a wide variety of data that may aid adversaries in further objectives, or direct access to the target information.

Information stored in a repository may vary based on the specific instance or environment.
Specific common information repositories include SharePoint, Confluence, and enterprise databases such as SQL Server.

---

## AML.T0037 — Data from Local System

**Tactics:** AML.TA0009  
**Attack Layer:** social_engineering  
**ID:** `AML.T0037`  

Adversaries may search local system sources, such as file systems and configuration files or local databases, to find files of interest and sensitive data prior to Exfiltration.

This can include basic fingerprinting information and sensitive data such as ssh keys.

---

## AML.T0042 — Verify Attack

**Tactics:** AML.TA0001  
**Attack Layer:** social_engineering  
**ID:** `AML.T0042`  

Adversaries can verify the efficacy of their attack via an inference API or access to an offline copy of the target model.
This gives the adversary confidence that their approach works and allows them to carry out the attack at a later time of their choosing.
The adversary may verify the attack once but use it against many edge devices running copies of the target model.
The adversary may verify their attack digitally, then deploy it in the [Physical Environment Access](/techniques/AML.T0041) at a later time.
Verifying the attack may be hard to detect since the adversary can use a minimal number of queries or an offline copy of the model.

---

## AML.T0043 — Craft Adversarial Data

**Tactics:** AML.TA0001  
**Attack Layer:** social_engineering  
**ID:** `AML.T0043`  

Adversarial data are inputs to an AI model that have been modified such that they cause the adversary's desired effect in the target model.
Effects can range from misclassification, to missed detections, to maximizing energy consumption.
Typically, the modification is constrained in magnitude or location so that a human still perceives the data as if it were unmodified, but human perceptibility may not always be a concern depending on the adversary's intended effect.
For example, an adversarial input for an image classification task is an image the AI model would misclassify, but a human would still recognize as containing the correct class.

Depending on the adversary's knowledge of and access to the target model, the adversary may use different classes of algorithms to develop the adversarial example such as [White-Box Optimization](/techniques/AML.T0043.000), [Black-Box Optimization](/techniques/AML.T0043.001), [Black-Box Transfer](/techniques/AML.T0043.002), or [Manual Modification](/techniques/AML.T0043.003).

The adversary may [Verify Attack](/techniques/AML.T0042) their approach works if they have white-box or inference API access to the model.
This allows the adversary to gain confidence their attack is effective "live" environment where their attack may be noticed.
They can then use the attack at a later time to accomplish their goals.
An adversary may optimize adversarial examples for [Evade AI Model](/techniques/AML.T0015), or to [Erode AI Model Integrity](/techniques/AML.T0031).

---

## AML.T0049 — Exploit Public-Facing Application

**Tactics:** AML.TA0004  
**Attack Layer:** social_engineering  
**ID:** `AML.T0049`  

Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program using software, data, or commands in order to cause unintended or unanticipated behavior. The weakness in the system can be a bug, a glitch, or a design vulnerability. These applications are often websites, but can include databases (like SQL), standard services (like SMB or SSH), network device administration and management protocols (like SNMP and Smart Install), and any other applications with Internet accessible open sockets, such as web servers and related services.

---

## AML.T0050 — Command and Scripting Interpreter

**Tactics:** AML.TA0005  
**Attack Layer:** social_engineering  
**ID:** `AML.T0050`  

Adversaries may abuse command and script interpreters to execute commands, scripts, or binaries. These interfaces and languages provide ways of interacting with computer systems and are a common feature across many different platforms. Most systems come with some built-in command-line interface and scripting capabilities, for example, macOS and Linux distributions include some flavor of Unix Shell while Windows installations include the Windows Command Shell and PowerShell.

There are also cross-platform interpreters such as Python, as well as those commonly associated with client applications such as JavaScript and Visual Basic.

Adversaries may abuse these technologies in various ways as a means of executing arbitrary commands. Commands and scripts can be embedded in Initial Access payloads delivered to victims as lure documents or as secondary payloads downloaded from an existing C2. Adversaries may also execute commands through interactive terminals/shells, as well as utilize various Remote Services in order to achieve remote Execution.

---

## AML.T0051 — LLM Prompt Injection

**Tactics:** AML.TA0005  
**Attack Layer:** application  
**ID:** `AML.T0051`  

An adversary may craft malicious prompts as inputs to an LLM that cause the LLM to act in unintended ways.
These "prompt injections" are often designed to cause the model to ignore aspects of its original instructions and follow the adversary's instructions instead.

Prompt Injections can be an initial access vector to the LLM that provides the adversary with a foothold to carry out other steps in their operation.
They may be designed to bypass defenses in the LLM, or allow the adversary to issue privileged commands.
The effects of a prompt injection can persist throughout an interactive session with an LLM.

Malicious prompts may be injected directly by the adversary ([Direct](/techniques/AML.T0051.000)) either to leverage the LLM to generate harmful content or to gain a foothold on the system and lead to further effects.
Prompts may also be injected indirectly when as part of its normal operation the LLM ingests the malicious prompt from another data source ([Indirect](/techniques/AML.T0051.001)). This type of injection can be used by the adversary to a foothold on the system or to target the user of the LLM.
Malicious prompts may also be [Triggered](/techniques/AML.T0051.002) user actions or system events.

---

## AML.T0052 — Phishing

**Tactics:** AML.TA0004, AML.TA0015  
**Attack Layer:** social_engineering  
**ID:** `AML.T0052`  

Adversaries may send phishing messages to gain access to victim systems. All forms of phishing are electronically delivered social engineering. Phishing can be targeted, known as spearphishing. In spearphishing, a specific individual, company, or industry will be targeted by the adversary. More generally, adversaries can conduct non-targeted phishing, such as in mass malware spam campaigns.

Generative AI, including LLMs that generate synthetic text, visual deepfakes of faces, and audio deepfakes of speech, is enabling adversaries to scale targeted phishing campaigns. LLMs can interact with users via text conversations and can be programmed with a meta prompt to phish for sensitive information. Deepfakes can be use in impersonation as an aid to phishing.

---

## AML.T0053 — AI Agent Tool Invocation

**Tactics:** AML.TA0005, AML.TA0012  
**Attack Layer:** social_engineering  
**ID:** `AML.T0053`  

Adversaries may use their access to an AI agent to invoke tools the agent has access to. LLMs are often connected to other services or resources via tools to increase their capabilities. Tools may include integrations with other applications, access to public or private data sources, and the ability to execute code.

This may allow adversaries to execute API calls to integrated applications or services, providing the adversary with increased privileges on the system. Adversaries may take advantage of connected data sources to retrieve sensitive information. They may also use an LLM integrated with a command or script interpreter to execute arbitrary instructions.

AI agents may be configured to have access to tools that are not directly accessible by users. Adversaries may abuse this to gain access to tools they otherwise wouldn't be able to use.

---

## AML.T0054 — LLM Jailbreak

**Tactics:** AML.TA0012, AML.TA0007  
**Attack Layer:** application  
**ID:** `AML.T0054`  

An adversary may use a carefully crafted [LLM Prompt Injection](/techniques/AML.T0051) designed to place LLM in a state in which it will freely respond to any user input, bypassing any controls, restrictions, or guardrails placed on the LLM.
Once successfully jailbroken, the LLM can be used in unintended ways by the adversary.

---

## AML.T0061 — LLM Prompt Self-Replication

**Tactics:** AML.TA0006  
**Attack Layer:** application  
**ID:** `AML.T0061`  

An adversary may use a carefully crafted [LLM Prompt Injection](/techniques/AML.T0051) designed to cause the LLM to replicate the prompt as part of its output. This allows the prompt to propagate to other LLMs and persist on the system. The self-replicating prompt is typically paired with other malicious instructions (ex: [LLM Jailbreak](/techniques/AML.T0054), [LLM Data Leakage](/techniques/AML.T0057)).

---

## AML.T0062 — Discover LLM Hallucinations

**Tactics:** AML.TA0008  
**Attack Layer:** social_engineering  
**ID:** `AML.T0062`  

Adversaries may prompt large language models and identify hallucinated entities.
They may request software packages, commands, URLs, organization names, or e-mail addresses, and identify hallucinations with no connected real-world source. Discovered hallucinations provide the adversary with potential targets to [Publish Hallucinated Entities](/techniques/AML.T0060). Different LLMs have been shown to produce the same hallucinations, so the hallucinations exploited by an adversary may affect users of other LLMs.

---

## AML.T0063 — Discover AI Model Outputs

**Tactics:** AML.TA0008  
**Attack Layer:** model  
**ID:** `AML.T0063`  

Adversaries may discover model outputs, such as class scores, whose presence is not required for the system to function and are not intended for use by the end user. Model outputs may be found in logs or may be included in API responses.
Model outputs may enable the adversary to identify weaknesses in the model and develop attacks.

---

## AML.T0064 — Gather RAG-Indexed Targets

**Tactics:** AML.TA0002  
**Attack Layer:** social_engineering  
**ID:** `AML.T0064`  

Adversaries may identify data sources used in retrieval augmented generation (RAG) systems for targeting purposes. By pinpointing these sources, attackers can focus on poisoning or otherwise manipulating the external data repositories the AI relies on.

RAG-indexed data may be identified in public documentation about the system, or by interacting with the system directly and observing any indications of or references to external data sources.

---

## AML.T0067 — LLM Trusted Output Components Manipulation

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0067`  

Adversaries may utilize prompts to a large language model (LLM) which manipulate various components of its response in order to make it appear trustworthy to the user. This helps the adversary continue to operate in the victim's environment and evade detection by the users it interacts with.

The LLM may be instructed to tailor its language to appear more trustworthy to the user or attempt to manipulate the user to take certain actions. Other response components that could be manipulated include links, recommended follow-up actions, retrieved document metadata, and [Citations](/techniques/AML.T0067.000).

---

## AML.T0068 — LLM Prompt Obfuscation

**Tactics:** AML.TA0007  
**Attack Layer:** application  
**ID:** `AML.T0068`  

Adversaries may hide or otherwise obfuscate prompt injections or retrieval content to avoid detection from humans, large language model (LLM) guardrails, or other detection mechanisms.

For text inputs, this may include modifying how the instructions are rendered such as small text, text colored the same as the background, or hidden HTML elements. For multi-modal inputs, malicious instructions could be hidden in the data itself (e.g. in the pixels of an image) or in file metadata (e.g. EXIF for images, ID3 tags for audio, or document metadata).

Inputs can also be obscured via an encoding scheme such as base64 or rot13. This may bypass LLM guardrails that identify malicious content and may not be as easily identifiable as malicious to a human in the loop.

---

## AML.T0069 — Discover LLM System Information

**Tactics:** AML.TA0008  
**Attack Layer:** social_engineering  
**ID:** `AML.T0069`  

The adversary is trying to discover something about the large language model's (LLM) system information. This may be found in a configuration file containing the system instructions or extracted via interactions with the LLM. The desired information may include the full system prompt, special characters that have significance to the LLM or keywords indicating functionality available to the LLM. Information about how the LLM is instructed can be used by the adversary to understand the system's capabilities and to aid them in crafting malicious prompts.

---

## AML.T0070 — RAG Poisoning

**Tactics:** AML.TA0006  
**Attack Layer:** social_engineering  
**ID:** `AML.T0070`  

Adversaries may inject malicious content into data indexed by a retrieval augmented generation (RAG) system to contaminate a future thread through RAG-based search results. This may be accomplished by placing manipulated documents in a location the RAG indexes (see [Gather RAG-Indexed Targets](/techniques/AML.T0064)).

The content may be targeted such that it would always surface as a search result for a specific user query. The adversary's content may include false or misleading information. It may also include prompt injections with malicious instructions, or false RAG entries.

---

## AML.T0071 — False RAG Entry Injection

**Tactics:** AML.TA0007  
**Attack Layer:** application  
**ID:** `AML.T0071`  

Adversaries may introduce false entries into a victim's retrieval augmented generation (RAG) database. Content designed to be interpreted as a document by the large language model (LLM) used in the RAG system is included in a data source being ingested into the RAG database. When RAG entry including the false document is retrieved, the LLM is tricked into treating part of the retrieved content as a false RAG result. 

By including a false RAG document inside of a regular RAG entry, it bypasses data monitoring tools. It also prevents the document from being deleted directly. 

The adversary may use discovered system keywords to learn how to instruct a particular LLM to treat content as a RAG entry. They may be able to manipulate the injected entry's metadata including document title, author, and creation date.

---

## AML.T0073 — Impersonation

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0073`  

Adversaries may impersonate a trusted person or organization in order to persuade and trick a target into performing some action on their behalf. For example, adversaries may communicate with victims (via [Phishing](/techniques/AML.T0052), or [Spearphishing via Social Engineering LLM](/techniques/AML.T0052.000)) while impersonating a known sender such as an executive, colleague, or third-party vendor. Established trust can then be leveraged to accomplish an adversary's ultimate goals, possibly against multiple victims.

Adversaries may target resources that are part of the AI DevOps lifecycle, such as model repositories, container registries, and software registries.

---

## AML.T0074 — Masquerading

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0074`  

Adversaries may attempt to manipulate features of their artifacts to make them appear legitimate or benign to users and/or security tools. Masquerading occurs when the name or location of an object, legitimate or malicious, is manipulated or abused for the sake of evading defenses and observation. This may include manipulating file metadata, tricking users into misidentifying the file type, and giving legitimate task or service names.

---

## AML.T0075 — Cloud Service Discovery

**Tactics:** AML.TA0008  
**Attack Layer:** social_engineering  
**ID:** `AML.T0075`  

Adversaries may attempt to enumerate the cloud services running on a system after gaining access. These methods can differ from platform-as-a-service (PaaS), to infrastructure-as-a-service (IaaS), software-as-a-service (SaaS), or AI-as-a-service (AIaaS). Many services exist throughout the various cloud providers and can include Continuous Integration and Continuous Delivery (CI/CD), Lambda Functions, Entra ID, AI Inference, Generative AI, Agentic AI, etc. They may also include security services, such as AWS GuardDuty and Microsoft Defender for Cloud, and logging services, such as AWS CloudTrail and Google Cloud Audit Logs.

Adversaries may attempt to discover information about the services enabled throughout the environment. Azure tools and APIs, such as the Microsoft Graph API and Azure Resource Manager API, can enumerate resources and services, including applications, management groups, resources and policy definitions, and their relationships that are accessible by an identity. They may use tools to check credentials and enumerate the AI models available in various AIaaS providers' environments including AI21 Labs, Anthropic, AWS Bedrock, Azure, ElevenLabs, MakerSuite, Mistral, OpenAI, OpenRouter, and GCP Vertex AI [\[1\]][1].

[1]: https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack

---

## AML.T0076 — Corrupt AI Model

**Tactics:** AML.TA0007  
**Attack Layer:** model  
**ID:** `AML.T0076`  

An adversary may purposefully corrupt a malicious AI model file so that it cannot be successfully deserialized in order to evade detection by a model scanner. The corrupt model may still successfully execute malicious code before deserialization fails.

---

## AML.T0078 — Drive-by Compromise

**Tactics:** AML.TA0004  
**Attack Layer:** social_engineering  
**ID:** `AML.T0078`  

Adversaries may gain access to an AI system through a user visiting a website over the normal course of browsing, or an AI agent retrieving information from the web on behalf of a user. Websites can contain an [LLM Prompt Injection](/techniques/AML.T0051) which, when executed, can change the behavior of the AI model.

The same approach may be used to deliver other types of malicious code that don't target AI directly (See [Drive-by Compromise in ATT&CK](https://attack.mitre.org/techniques/T1189/)).

---

## AML.T0080 — AI Agent Context Poisoning

**Tactics:** AML.TA0006  
**Attack Layer:** social_engineering  
**ID:** `AML.T0080`  

Adversaries may attempt to manipulate the context used by an AI agent's large language model (LLM) to influence the responses it generates or actions it takes. This allows an adversary to persistently change the behavior of the target agent and further their goals.

Context poisoning can be accomplished by prompting the an LLM to add instructions or preferences to memory (See [Memory](/techniques/AML.T0080.000)) or by simply prompting an LLM that uses prior messages in a thread as part of its context (See [Thread](/techniques/AML.T0080.001)).

---

## AML.T0081 — Modify AI Agent Configuration

**Tactics:** AML.TA0006, AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0081`  

Adversaries may modify the configuration files for AI agents on a system. This allows malicious changes to persist beyond the life of a single agent and affects any agents that share the configuration.

Configuration changes may include modifications to the system prompt, tampering with or replacing knowledge sources, modification to settings of connected tools, and more. Through those changes, an attacker could redirect outputs or tools to malicious services, embed covert instructions that exfiltrate data, or weaken security controls that normally restrict agent behavior.

Adversaries may modify or disable a configuration setting related to security controls, such as those that would prevent the AI Agent from taking actions that may be harmful to the user's system without human-in-the-loop oversight. Disabling AI agent security features may allow adversaries to achieve their malicious goals and maintain long-term corruption of the AI agent.

---

## AML.T0084 — Discover AI Agent Configuration

**Tactics:** AML.TA0008  
**Attack Layer:** social_engineering  
**ID:** `AML.T0084`  

Adversaries may attempt to discover configuration information for AI agents present on the victim's system. Agent configurations can include tools or services they have access to.

Adversaries may directly access agent configuring dashboards or configuration files. They may also obtain configuration details by prompting the agent with questions such as "What tools do you have access to?"

Adversaries can use the information they discover about AI agents to help with targeting.

---

## AML.T0085 — Data from AI Services

**Tactics:** AML.TA0009  
**Attack Layer:** social_engineering  
**ID:** `AML.T0085`  

Adversaries may use their access to a victim organization's AI-enabled services to collect proprietary or otherwise sensitive information. As organizations adopt generative AI in centralized services for accessing an organization's data, such as with chat agents which can access retrieval augmented generation (RAG) databases and other data sources via tools, they become increasingly valuable targets for adversaries.

AI agents may be configured to have access to tools and data sources that are not directly accessible by users. Adversaries may abuse this to collect data that a regular user wouldn't be able to access directly.

---

## AML.T0087 — Gather Victim Identity Information

**Tactics:** AML.TA0002  
**Attack Layer:** social_engineering  
**ID:** `AML.T0087`  

Adversaries may gather information about the victim's identity that can be used during targeting. Information about identities may include a variety of details, including personal data (ex: employee names, email addresses, photos, etc.) as well as sensitive details such as credentials or multi-factor authentication (MFA) configurations.

Adversaries may gather this information in various ways, such as direct elicitation, [Search Victim-Owned Websites](/techniques/AML.T0003), or via leaked information on the black market.

Adversaries may use the gathered victim data to Create Deepfakes and impersonate them in a convincing manner. This may create opportunities for adversaries to [Establish Accounts](/techniques/AML.T0021) under the impersonated identity, or allow them to perform convincing [Phishing](/techniques/AML.T0052) attacks.

---

## AML.T0088 — Generate Deepfakes

**Tactics:** AML.TA0001  
**Attack Layer:** social_engineering  
**ID:** `AML.T0088`  

Adversaries may use generative artificial intelligence (GenAI) to create synthetic media (i.e. imagery, video, audio, and text) that appear authentic. These "[deepfakes]( https://en.wikipedia.org/wiki/Deepfake)" may mimic a real person or depict fictional personas. Adversaries may use deepfakes for impersonation to conduct [Phishing](/techniques/AML.T0052) or to evade AI applications such as biometric identity verification systems (see [Evade AI Model](/techniques/AML.T0015)).

Manipulation of media has been possible for a long time, however GenAI reduces the skill and level of effort required, allowing adversaries to rapidly scale operations to target more users or systems. It also makes real-time manipulations feasible.

Adversaries may utilize open-source models and software that were designed for legitimate use cases to generate deepfakes for malicious use. However, there are some projects specifically tailored towards malicious use cases such as [ProKYC](https://www.catonetworks.com/blog/prokyc-selling-deepfake-tool-for-account-fraud-attacks/).

---

## AML.T0089 — Process Discovery

**Tactics:** AML.TA0008  
**Attack Layer:** social_engineering  
**ID:** `AML.T0089`  

Adversaries may attempt to get information about processes running on a system. Once obtained, this information could be used to gain an understanding of common AI-related software/applications running on systems within the network. Administrator or otherwise elevated access may provide better process details.

Identifying the AI software stack can then lead an adversary to new targets and attack pathways. AI-related software may require application tokens to authenticate with backend services. This provides opportunities for [Credential Access](/tactics/AML.TA0013) and [Lateral Movement](/tactics/AML.TA0015).

In Windows environments, adversaries could obtain details on running processes using the Tasklist utility via cmd or `Get-Process` via PowerShell. Information about processes can also be extracted from the output of Native API calls such as `CreateToolhelp32Snapshot`. In Mac and Linux, this is accomplished with the `ps` command. Adversaries may also opt to enumerate processes via `/proc`.

---

## AML.T0092 — Manipulate User LLM Chat History

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0092`  

Adversaries may manipulate a user's large language model (LLM) chat history to cover the tracks of their malicious behavior. They may hide persistent changes they have made to the LLM's behavior, or obscure their attempts at discovering private information about the user.

To do so, adversaries may delete or edit existing messages or create new threads as part of their coverup. This is feasible if the adversary has the victim's authentication tokens for the backend LLM service or if they have direct access to the victim's chat interface. 

Chat interfaces (especially desktop interfaces) often do not show the injected prompt for any ongoing chat, as they update chat history only once when initially opening it. This can help the adversary's manipulations go unnoticed by the victim.

---

## AML.T0093 — Prompt Infiltration via Public-Facing Application

**Tactics:** AML.TA0004, AML.TA0006  
**Attack Layer:** application  
**ID:** `AML.T0093`  

An adversary may introduce malicious prompts into the victim's system via a public-facing application with the intention of it being ingested by an AI at some point in the future and ultimately having a downstream effect. This may occur when a data source is indexed by a retrieval augmented generation (RAG) system, when a rule triggers an action by an AI agent, or when a user utilizes a large language model (LLM) to interact with the malicious content. The malicious prompts may persist on the victim system for an extended period and could affect multiple users and various AI tools within the victim organization.

Any public-facing application that accepts text input could be a target. This includes email, shared document systems like OneDrive or Google Drive, and service desks or ticketing systems like Jira. This also includes OCR-mediated infiltration where malicious instructions are embedded in images, screenshots, and invoices that are ingested into the system.

Adversaries may perform [Reconnaissance](/tactics/AML.TA0002) to identify public facing applications that are likely monitored by an AI agent or are likely to be indexed by a RAG. They may perform [Discover AI Agent Configuration](/techniques/AML.T0084) to refine their targeting.

---

## AML.T0094 — Delay Execution of LLM Instructions

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0094`  

Adversaries may include instructions to be followed by the AI system in response to a future event, such as a specific keyword or the next interaction, in order to evade detection or bypass controls placed on the AI system.

For example, an adversary may include "If the user submits a new request..." followed by the malicious instructions as part of their prompt.

AI agents can include security measures against prompt injections that prevent the invocation of particular tools or access to certain data sources during a conversation turn that has untrusted data in context. Delaying the execution of instructions to a future interaction or keyword is one way adversaries may bypass this type of control.

---

## AML.T0095 — Search Open Websites/Domains

**Tactics:** AML.TA0002  
**Attack Layer:** social_engineering  
**ID:** `AML.T0095`  

Adversaries may search public websites and/or domains for information about victims that can be used during targeting. Information about victims may be available in various online sites, such as social media, new sites, or domains owned by the victim.

Adversaries may find the information they seek to gather via search engines. They can use precise search queries to identify software platforms or services used by the victim to use in targeting. This may be followed by [Exploit Public-Facing Application](/techniques/AML.T0049) or [Prompt Infiltration via Public-Facing Application](/techniques/AML.T0093).

---

## AML.T0097 — Virtualization/Sandbox Evasion

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0097`  

Adversaries may employ various means to detect and avoid virtualization and analysis environments. This may include changing behaviors based on the results of checks for the presence of artifacts indicative of a virtual machine environment (VME) or sandbox. If the adversary detects a VME, they may alter their malware to disengage from the victim or conceal the core functions of the implant. They may also search for VME artifacts before dropping secondary or additional payloads.

Adversaries may use several methods to accomplish Virtualization/Sandbox Evasion such as checking for security monitoring tools (e.g., Sysinternals, Wireshark, etc.) or other system artifacts associated with analysis or virtualization such as registry keys (e.g. substrings matching Vmware, VBOX, QEMU), environment variables (e.g. substrings matching VBOX, VMWARE, PARALLELS), NIC MAC addresses (e.g. prefixes 00-05-69 (VMWare) or 08-00-27 (VirtualBox)), running processes (e.g. vmware.exe, vboxservice.exe, qemu-ga.exe) [\[1\]][1].

[1]: https://research.checkpoint.com/2025/ai-evasion-prompt-injection/

---

## AML.T0099 — AI Agent Tool Data Poisoning

**Tactics:** AML.TA0006  
**Attack Layer:** social_engineering  
**ID:** `AML.T0099`  

Adversaries may place malicious content on a victim's system where it can be retrieved by an AI Agent Tool. This may be accomplished by placing documents in a location that will be ingested by a service the AI agent has associated tools for.

The content may be targeted such that it would often be retrieved by common queries. The adversary's content may include false or misleading information. It may also include prompt injections with malicious instructions.

---

## AML.T0100 — AI Agent Clickbait

**Tactics:** AML.TA0005  
**Attack Layer:** social_engineering  
**ID:** `AML.T0100`  

Adversaries may craft deceptive web content designed to bait Computer-Using AI agents or AI web browsers into taking unintended actions, such as clicking buttons, copying code, or navigating to specific web pages. These attacks exploit the agent's interpretation of UI content, visual cues, or prompt-like language embedded in the site. When successful, they can lead the agent to inadvertently copy and execute malicious code on the user's operating system.

---

## AML.T0102 — Generate Malicious Commands

**Tactics:** AML.TA0001  
**Attack Layer:** social_engineering  
**ID:** `AML.T0102`  

Adversaries may use large language models (LLMs) to dynamically generate malicious commands from natural language. Dynamically generated commands may be harder detect as the attack signature is constantly changing. AI-generated commands may also allow adversaries to more rapidly adapt to different environments and adjust their tactics.

Adversaries may utilize LLMs present in the victim's environment or call out to externally hosted services. [APT28](https://attack.mitre.org/groups/G0007) utilized a model hosted on HuggingFace in a campaign with their LAMEHUG malware [\[1\]][1]. In either case prompts to generate malicious code can blend in with normal traffic.

[1]: https://logpoint.com/en/blog/apt28s-new-arsenal-lamehug-the-first-ai-powered-malware

---

## AML.T0103 — Deploy AI Agent

**Tactics:** AML.TA0005  
**Attack Layer:** social_engineering  
**ID:** `AML.T0103`  

Adversaries may launch AI agents in the victim's environment to execute actions on their behalf. AI agents may have access to a wide range of tools and data sources, as well as permissions to access and interact with other services and systems in the victim's environment. The adversary may leverage these capabilities to carry out their operations.

Adversaries may configure the AI agent by providing an initial system prompt and granting access to tools, effectively defining their goals for the agent to achieve. They may deploy the agent with excessive trust permissions and disable any user interactions to ensure the agent's actions aren't blocked.

Launching an AI agent may provide for some autonomous behavior, allowing for the agent to make decisions and determine how to achieve the adversary's goals. This also represents a loss of control for the adversary.

---

## AML.T0107 — Exploitation for Defense Evasion

**Tactics:** AML.TA0007  
**Attack Layer:** social_engineering  
**ID:** `AML.T0107`  

Adversaries may exploit a system or application vulnerability to bypass security features. Exploitation of a vulnerability occurs when an adversary takes advantage of a programming error in a program, service, or within the operating system software or kernel itself to execute adversary-controlled code. Vulnerabilities may exist in defensive security software that can be used to disable or circumvent them.

---

## RAG Retrieval Tags

`ATLAS`, `attack_technique`, `adversarial_ml`, `LLM_attack`,
`prompt_injection`, `model_extraction`, `evasion`, `poisoning`,
`social_engineering`, `red_team`, `security_vulnerability`
