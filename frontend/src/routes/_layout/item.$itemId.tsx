import { createFileRoute } from '@tanstack/react-router'
import  UploadBox  from '@/components/ui/UploadBox'
import SummaryResult from "@/components/ui/SummaryResult"

import { useState } from 'react'

export const Route = createFileRoute('/_layout/item/$itemId')({
  component: RouteComponent,
})

function RouteComponent() {
  const [summary, setSummary] = useState<string>(" ")



  return (
  <>
    <div style={{ display: "flex", flexDirection: "row", gap: "20px", paddingBottom: "20px", marginBottom: "20px", paddingTop: "20px", height: "100%"}}>
      <UploadBox onUploadStart={() => setSummary(" ")} onUploadSuccess={(text) => setSummary(text)} />
      <SummaryResult content={summary} />
    </div>
    
  </>
  )
}
