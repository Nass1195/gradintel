import { createFileRoute } from '@tanstack/react-router'
import { useState } from 'react'
import { fileUploadService } from "@/client"
import { Button } from "@chakra-ui/react"
export const Route = createFileRoute('/_layout/evaluate')({
  component: RouteComponent,
})

function RouteComponent() {
  const [status, setStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');

  const runEvaluation = async () => {
    setStatus('running');
    await fileUploadService.runEvaluation()
    setStatus('completed')
 
  };

  return (

    <Button
      onClick={runEvaluation}
      disabled={status === 'running'}
    >
      {status === 'running' ? 'Running Pipeline...' : 'Run Evaluation Pipeline'}
    </Button>


  );
}