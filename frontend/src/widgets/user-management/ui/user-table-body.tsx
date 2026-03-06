/**
 * CLOVA Tutor
 * Copyright (c) 2026-present NAVER Cloud Corp.
 * MIT
 */

import { useQueryClient, useSuspenseQuery } from '@tanstack/react-query';

import { useRouter, useSearch } from '@tanstack/react-router';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { usersQueries } from '@/entities/users/__generated__/api/queries';
import { gradeToName } from '@/entities/users/utils/user-grade';
import type { UserResponseDto } from '@/shared/api/__generated__/dto';
import { LOCAL_STORAGE_KEY } from '@/shared/constants/storage-key';
import { Badge } from '@/shared/ui/badge';
import { TableBody, TableCell, TableRow } from '@/shared/ui/table';
import { UserTableRowActions } from './_user-table-row-actions';

export function UserTableBody() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { username } = useSearch({ from: '/login/' });
  const { data: users } = useSuspenseQuery({
    ...usersQueries.getUsers({}),
    select: (data) =>
      username ? data.filter((user) => user.name.toLowerCase().includes(username.toLowerCase())) : data,
  });

  const handleLogin = async (user: UserResponseDto) => {
    localStorage.setItem(LOCAL_STORAGE_KEY.USER_ID, user.id);
    await queryClient.invalidateQueries();
    router.navigate({ to: '/', replace: true });
    toast.success(`${user.name}계정으로 로그인되었습니다.`, {
      duration: 3000,
      position: 'top-center',
    });
  };

  if (users.length === 0) {
    return (
      <TableBody>
        <TableRow>
          <TableCell colSpan={5} className="text-center text-muted-foreground text-sm py-12">
            생성된 계정이 없습니다. 새로운 계정을 생성해주세요.
          </TableCell>
        </TableRow>
      </TableBody>
    );
  }

  return (
    <TableBody>
      {users.map((user) => (
        <TableRow key={user.id}>
          <TableCell className="ps-11 hover:underline cursor-pointer" onClick={() => handleLogin(user)}>
            {user.name}
          </TableCell>
          <TableCell>
            <Badge variant="secondary">{gradeToName(user.grade)}</Badge>
          </TableCell>
          <TableCell className="text-muted-foreground">{format(new Date(user.created_at), 'yyyy-MM-dd')}</TableCell>
          <TableCell className="text-muted-foreground">{format(new Date(user.updated_at), 'yyyy-MM-dd')}</TableCell>
          <TableCell className="w-10 pe-8">
            <UserTableRowActions user={user} />
          </TableCell>
        </TableRow>
      ))}
    </TableBody>
  );
}
