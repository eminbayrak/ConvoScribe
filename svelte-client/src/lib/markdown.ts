import { marked } from 'marked';
import Prism from 'prismjs';

// Import common language components for syntax highlighting (only core ones to avoid build issues)
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-bash';

// Language aliases mapping common names to Prism language identifiers
const languageAliases: Record<string, string> = {
    'js': 'javascript',
    'ts': 'typescript',
    'py': 'python',
    'sh': 'bash',
    'shell': 'bash',
    'cmd': 'bash',
    'powershell': 'bash',
    'ps1': 'bash',
    'cs': 'csharp',
    'c++': 'cpp',
    'c#': 'csharp',
    'jsx': 'javascript',
    'tsx': 'typescript',
    'vue': 'html',
    'svelte': 'html',
    'htm': 'html',
    'yml': 'yaml',
    'dockerfile': 'docker',
    'conf': 'nginx'
};

// Get the actual Prism language name from user input
function getPrismLanguage(lang: string): string {
    const normalizedLang = lang.toLowerCase().trim();
    return languageAliases[normalizedLang] || normalizedLang;
}

// Custom renderer for code blocks with syntax highlighting
const renderer = new marked.Renderer();

renderer.code = function ({ text, lang, escaped }: { text: string; lang?: string; escaped?: boolean; }): string {
    const isEscaped = escaped || false;

    if (!lang) {
        // No language specified, render as plain text with basic styling
        return `<pre class="code-block"><code class="code-plain">${isEscaped ? text : Prism.util.encode(text)}</code></pre>`;
    }

    const prismLang = getPrismLanguage(lang);

    // Check if Prism has this language
    if (Prism.languages[prismLang]) {
        try {
            const highlighted = Prism.highlight(text, Prism.languages[prismLang], prismLang);
            return `<pre class="code-block" data-language="${prismLang}"><code class="language-${prismLang}">${highlighted}</code></pre>`;
        } catch (error) {
            console.warn(`Failed to highlight code for language "${prismLang}":`, error);
        }
    }

    // Fallback to plain text with language label
    return `<pre class="code-block" data-language="${prismLang}"><code class="code-plain">${isEscaped ? text : Prism.util.encode(text)}</code></pre>`;
};

// Custom renderer for inline code
renderer.codespan = function ({ text }: { text: string; }): string {
    return `<code class="code-inline">${Prism.util.encode(text)}</code>`;
};

// Configure marked with our custom renderer
marked.setOptions({
    renderer: renderer,
    gfm: true, // GitHub Flavored Markdown
    breaks: false // Don't break on single line breaks
});

// Export the configured marked instance
export { marked };

// Export Prism for direct use if needed
export { Prism };
