import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Pizza",
    titleTemplate: ":title · Pizza",
    lang: "en-US",
    lastUpdated: true,
    description: "Metadata that leaves a good aftertaste.",
    head: [["link", { rel: "icon", href: "/pizza.png" }]],
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        logo: "/pizza.png",
        nav: [
            { text: "Home", link: "/" },
            { text: "Get Started", link: "/getting-started" },
            { text: "FAQ", link: "/faq" }
        ],
        sidebar: [
            {
                text: "Getting Started",
                items: [
                    { text: "Installation", link: "/getting-started/installation" },
                    { text: "Basic Usage", link: "/getting-started/basic-usage" }
                ]
            },
            {
                text: "CLI",
                items: [
                    { text: "Database management", link: "/cli/database-management" },
                    { text: "Metadata handling", link: "/cli/metadata-handling" }
                ]
            },
            { text: "FAQ", link: "/faq" }
        ],
        socialLinks: [
            { icon: "github", link: "https://github.com/iiPythonx/pizza" }
        ]
    }
})
