import { createFileRoute } from "@tanstack/react-router"
import UploadBox from "@/components/ui/UploadBox"
import { useState} from "react"
import SummaryResult from "@/components/ui/SummaryResult"
import { ItemCard } from "@/components/ui/DashboardCards"



export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})


function Dashboard() {
  const [summary, setSummary] = useState<string>("")
  return (<>
  <ItemCard title="Sample Item" summarySnippet="This is a sample summary snippet for the item card. It provides a brief overview of the item's content." date="2024-06-01" />
    <UploadBox onUploadStart={() => setSummary("aa")} onUploadSuccess={(text) => setSummary(text)}/>
    <SummaryResult content={summary} />
  </>)
}
