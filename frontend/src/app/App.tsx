/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { RouterProvider } from '@tanstack/react-router';
import { router } from '@/app/routes/router.tsx';

function App() {
  return <RouterProvider router={router} />;
}

export default App;
