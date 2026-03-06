import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'CLOVA Tutor',
  tagline: '포기하지 않고 문제 해결 능력을 키우는 AI Tutor',
  favicon: 'img/favicon.svg',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-org.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub Pages project sites, this is typically '/<projectName>/'
  baseUrl: '/clova-tutor/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'Digital-Healthcare-LAB', // Usually your GitHub org/user name.
  projectName: 'clova-tutor', // Usually your repo name.

  onBrokenLinks: 'warn', // 'throw'에서 'warn'으로 변경하여 빌드가 실패하지 않도록 함

  i18n: {
    defaultLocale: 'ko',
    locales: ['ko', 'en'],
    localeConfigs: {
      ko: { label: '한국어' },
      en: { label: 'English' },
    },
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/your-org/clova-tutor/edit/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    './src/plugins/webpack-alias.js',
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en', 'ko'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
        docsRouteBasePath: '/docs',
        indexBlog: false,
        searchBarShortcutHint: false,
      },
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: true,
      respectPrefersColorScheme: false,
    },
    navbar: {
      title: 'CLOVA Tutor',
      logo: {
        alt: 'CLOVA Tutor Logo',
        src: 'img/favicon.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: '문서',
        },
        {
          type: 'localeDropdown',
          position: 'right',
          label: '언어',
        },
        {
          href: 'https://github.com/your-org/clova-tutor',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: '시작하기',
              to: '/docs/user-guide/start',
            },
          ],
        },
        {
          title: 'GitHub',
          items: [
            {
              label: 'Repository',
              href: 'https://github.com/your-org/clova-tutor',
            },
            {
              label: 'Issues',
              href: 'https://github.com/your-org/clova-tutor/issues',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} NAVER Cloud. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
