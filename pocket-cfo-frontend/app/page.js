'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSession } from 'next-auth/react';
import { RefreshCw } from 'lucide-react';

export default function HomeRedirect() {
  const router = useRouter();
  const { status } = useSession();

  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/login");
    } else if (status === "authenticated") {
      router.push("/dashboard");
    }
  }, [status, router]);

  return (
    <div className="min-h-screen bg-[#0D0F12] flex items-center justify-center">
      <RefreshCw size={32} className="text-amber-500 animate-spin" />
    </div>
  );
}
