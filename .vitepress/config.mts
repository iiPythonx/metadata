import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Pizza",
    titleTemplate: ":title · Pizza",
    lang: "en-US",
    lastUpdated: true,
    description: "Metadata that leaves a good aftertaste.",
    head: [["link", { rel: "icon", href: "/pizza.png" }], ["meta", { name: "darkreader-lock" }]],
    cleanUrls: true,
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        logo: "/pizza.png",
        nav: [
            { text: "Home", link: "/" },
            {
                text: "Documentation",
                items: [
                    { text: "Getting Started", link: "/intro/what-is-pizza" },
                    { text: "CLI", link: "/cli/indexing" }
                ]
            },
            { text: "FAQ", link: "/faq" }
        ],
        sidebar: [
            {
                text: "Introduction",
                collapsed: false,
                items: [
                    { text: "What is Pizza?", link: "/intro/what-is-pizza" },
                    { text: "Getting Started", link: "/intro/getting-started" }
                ]
            },
            {
                text: "CLI",
                collapsed: false,
                items: [
                    { text: "Indexing", link: "/cli/indexing" },
                    { text: "Metadata writing", link: "/cli/metadata" },
                    { text: "Debugging", link: "/cli/debugging" },
                    { text: "Extras", link: "/cli/extras" }
                ]
            },
            { text: "FAQ", link: "/faq" }
        ],
        socialLinks: [
            { icon: "github", link: "https://github.com/iiPythonx/pizza" }
        ]
    }
})
