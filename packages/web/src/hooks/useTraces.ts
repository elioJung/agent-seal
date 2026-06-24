import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getTraces, issueCertificate } from '../lib/api'

export function useTraces(page = 1, enabled = true) {
  return useQuery({
    queryKey: ['traces', page],
    queryFn: () => getTraces(page),
    enabled,
    refetchInterval: 5000,
  })
}

export function useIssueCertificate() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (traceId: string) => issueCertificate(traceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traces'] })
    },
  })
}
