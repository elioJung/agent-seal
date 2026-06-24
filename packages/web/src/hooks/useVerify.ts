import { useQuery } from '@tanstack/react-query'
import { verifyCertificate } from '../lib/api'

export function useVerify(certId: string) {
  return useQuery({
    queryKey: ['verify', certId],
    queryFn: () => verifyCertificate(certId),
    enabled: !!certId,
    retry: false,
  })
}
