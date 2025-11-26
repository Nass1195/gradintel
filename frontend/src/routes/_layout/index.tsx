import { createFileRoute } from "@tanstack/react-router"
import UploadBox from "@/components/ui/UploadBox"
import { useState} from "react"
import SummaryResult from "@/components/ui/SummaryResult"



export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})


function Dashboard() {
  const [summary, setSummary] = useState<string>("")
  return (<>
    <UploadBox onUploadStart={() => setSummary("aa")} onUploadSuccess={(text) => setSummary(text)}/>
    <SummaryResult content={summary} />
  </>)
}
