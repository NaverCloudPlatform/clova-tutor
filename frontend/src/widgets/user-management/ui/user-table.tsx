/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { Table, TableHead, TableHeader, TableRow } from '@/shared/ui/table';
import { UserTableBody } from './user-table-body';

export function UserTable() {
  return (
    <div className="border rounded-md bg-card">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="ps-11">이름</TableHead>
            <TableHead>학년</TableHead>
            <TableHead>생성 일자</TableHead>
            <TableHead>수정 일자</TableHead>
            <TableHead className="w-10 pe-8" />
          </TableRow>
        </TableHeader>
        <UserTableBody />
      </Table>
    </div>
  );
}
