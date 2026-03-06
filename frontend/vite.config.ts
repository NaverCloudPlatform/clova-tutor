import path from 'node:path';
import tailwindcss from '@tailwindcss/vite';
import { TanStackRouterVite } from '@tanstack/router-plugin/vite';
import react from '@vitejs/plugin-react';
import { defineConfig, type Plugin } from 'vite';

/**
 * KaTeX 폰트 최적화 플러그인
 *
 * 참고: https://katex.org/docs/font
 * - KaTeX는 Sass 변수($use-woff2: true)로도 설정 가능하지만
 *   현재 프로젝트는 CSS만 사용하므로 Vite 플러그인 방식 채택
 * - woff2만 유지하고 woff, ttf는 제거하여 번들 크기 최적화
 */
function excludeKatexFonts(): Plugin {
  return {
    name: 'exclude-katex-fonts',
    enforce: 'pre',
    transform(code, id) {
      if (!id.includes('katex') || !id.endsWith('.css')) return;

      const transformed = code
        // .woff2는 유지하고 .woff, .ttf만 제거
        .replace(/url\([^)]*\.woff(?!2)\)\s*format\([^)]*\),?\s*/g, '')
        .replace(/url\([^)]*\.ttf\)\s*format\([^)]*\),?\s*/g, '')
        .replace(/,(\s*;)/g, '$1');

      return {
        code: transformed,
        map: null,
      };
    },
  };
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    TanStackRouterVite({
      target: 'react',
      autoCodeSplitting: true,
      routesDirectory: './src/pages',
      generatedRouteTree: './src/app/routes/routeTree.gen.ts',
      routeFileIgnorePattern: '(?:^|/)-[^/]+/',
    }),
    react(),
    tailwindcss(),
    excludeKatexFonts(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~': path.resolve(__dirname, '.'),
    },
  },
  build: {
    target: 'esnext',
  },
  optimizeDeps: {
    entries: ['index.html', 'src/**/*.{ts,tsx}'],
    exclude: ['playwright'],
  },
  server: {
    host: true,
    watch: {
      ignored: ['**/playwright/**'],
    },
  },
  cacheDir: '.vite',
  publicDir: 'public',
});
