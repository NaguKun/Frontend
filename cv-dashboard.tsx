"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Upload, Search, MapPin, Mail, Phone, Calendar, User, FileText, Moon, Sun, ExternalLink } from "lucide-react"
import { useTheme } from "next-themes"

// Mock data structure based on your provided format
const mockCandidates = [
  {
    full_name: "Tu Mai The Nhan",
    email: "nhan.tu2107@gmail.com",
    phone: "0865684801",
    location: "Ho Chi Minh City",
    id: 1,
    created_at: "2025-06-02T08:27:13.646321Z",
    updated_at: null,
    skills: [
      { name: "HTML" },
      { name: "Neo4j" },
      { name: "NumPy" },
      { name: "React Native" },
      { name: "Git" },
      { name: "C++" },
      { name: "Scikit-Learn" },
      { name: "Flutter" },
      { name: "LangChain" },
      { name: "Ruby" },
      { name: "Pandas" },
      { name: "FastAPI" },
      { name: "Docker" },
      { name: "MQTT" },
      { name: "ReactJS" },
      { name: "SQL" },
      { name: "Python" },
      { name: "TensorFlow" },
      { name: "Machine Learning" },
      { name: "Deep Learning" },
    ],
    cv_file_id: "199cBPeXGHG3eSUnQGwgCS0ajOl3pQN37",
  },
  {
    full_name: "Yunlong Jiao",
    email: "yljiao.ustc@gmail.com",
    phone: "+44 7400 724281",
    location: "London, UK",
    id: 2,
    created_at: "2025-06-02T13:54:01.783462Z",
    updated_at: null,
    skills: [
      { name: "Python (numpy, pandas, scikit-learn)" },
      { name: "Large Language Models" },
      { name: "Feature Engineering" },
      { name: "Agile Development" },
      { name: "Cloud Computing (AWS, SageMaker)" },
      { name: "SQL" },
      { name: "Information Extraction" },
      { name: "R" },
      { name: "Model Development" },
      { name: "Deep Learning Frameworks (PyTorch, MXNet)" },
      { name: "Natural Language Processing" },
      { name: "Python" },
      { name: "Neural Text-to-Speech" },
      { name: "C/C++" },
    ],
    cv_file_id: "1pKDqCeElqc4nK2OO4unz3DnflUAyDRVN",
  },
]

interface Candidate {
  full_name: string
  email: string
  phone: string
  location: string
  id: number
  created_at: string
  updated_at: string | null
  skills: { name: string }[]
  cv_file_id: string
}

function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
      className="border-green-200 hover:bg-green-50 hover:border-green-300 dark:border-green-800 dark:hover:bg-green-950"
    >
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}

export default function CVDashboard() {
  const [uploadedCV, setUploadedCV] = useState<Candidate | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [locationFilter, setLocationFilter] = useState("")
  const [skillFilter, setSkillFilter] = useState("")
  const [candidates] = useState<Candidate[]>(mockCandidates)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Simulate CV processing and data extraction
      const mockExtractedData: Candidate = {
        full_name: "John Doe",
        email: "john.doe@example.com",
        phone: "+1 234 567 8900",
        location: "New York, USA",
        id: Date.now(),
        created_at: new Date().toISOString(),
        updated_at: null,
        skills: [
          { name: "JavaScript" },
          { name: "React" },
          { name: "Node.js" },
          { name: "TypeScript" },
          { name: "Python" },
          { name: "AWS" },
        ],
        cv_file_id: `${Date.now()}mockFileId`,
      }
      setUploadedCV(mockExtractedData)
    }
  }

  const filteredCandidates = candidates.filter((candidate) => {
    const matchesSearch =
      searchQuery === "" ||
      candidate.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      candidate.skills.some((skill) => skill.name.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesLocation =
      locationFilter === "" || candidate.location.toLowerCase().includes(locationFilter.toLowerCase())

    const matchesSkill =
      skillFilter === "" ||
      candidate.skills.some((skill) => skill.name.toLowerCase().includes(skillFilter.toLowerCase()))

    return matchesSearch && matchesLocation && matchesSkill
  })

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  const CandidateCard = ({ candidate }: { candidate: Candidate }) => (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              {candidate.full_name}
            </CardTitle>
            <CardDescription className="flex items-center gap-4 mt-2">
              <span className="flex items-center gap-1">
                <Mail className="h-4 w-4" />
                {candidate.email}
              </span>
              <span className="flex items-center gap-1">
                <Phone className="h-4 w-4" />
                {candidate.phone}
              </span>
            </CardDescription>
          </div>
          <Badge variant="outline" className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {candidate.location}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Added: {formatDate(candidate.created_at)}</span>
            <Separator orientation="vertical" className="h-4" />
            <FileText className="h-4 w-4" />
            <Button
              variant="link"
              size="sm"
              asChild
              className="h-auto p-0 text-sm text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
            >
              <a
                href={`https://drive.google.com/file/d/${candidate.cv_file_id}/view`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1"
              >
                View CV <ExternalLink className="h-3 w-3" />
              </a>
            </Button>
          </div>

          <div>
            <Label className="text-sm font-medium">Skills ({candidate.skills.length})</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {candidate.skills.slice(0, 10).map((skill, index) => (
                <Badge
                  key={index}
                  className="text-xs bg-green-100 text-green-800 hover:bg-green-200 dark:bg-green-900 dark:text-green-100"
                >
                  {skill.name}
                </Badge>
              ))}
              {candidate.skills.length > 10 && (
                <Badge
                  variant="outline"
                  className="text-xs border-green-300 text-green-700 dark:border-green-700 dark:text-green-300"
                >
                  +{candidate.skills.length - 10} more
                </Badge>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">CV Management Dashboard</h1>
            <p className="text-muted-foreground mt-2">Upload and manage candidate CVs with intelligent search</p>
          </div>
          <ThemeToggle />
        </div>
      </div>

      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-green-50 dark:bg-green-950">
          <TabsTrigger
            value="upload"
            className="flex items-center gap-2 data-[state=active]:bg-green-600 data-[state=active]:text-white"
          >
            <Upload className="h-4 w-4" />
            Upload CV
          </TabsTrigger>
          <TabsTrigger
            value="search"
            className="flex items-center gap-2 data-[state=active]:bg-green-600 data-[state=active]:text-white"
          >
            <Search className="h-4 w-4" />
            Search & Filter
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Upload New CV</CardTitle>
              <CardDescription>Upload a CV file to extract candidate information automatically</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                  <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <div className="space-y-2">
                    <Label htmlFor="cv-upload" className="text-lg font-medium cursor-pointer">
                      Click to upload or drag and drop
                    </Label>
                    <p className="text-sm text-muted-foreground">PDF, DOC, DOCX files up to 10MB</p>
                  </div>
                  <Input
                    id="cv-upload"
                    type="file"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                  <Button asChild className="mt-4 bg-green-600 hover:bg-green-700">
                    <Label htmlFor="cv-upload" className="cursor-pointer">
                      Choose File
                    </Label>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {uploadedCV && (
            <div className="space-y-4">
              <h3 className="text-xl font-semibold">Extracted CV Data</h3>
              <CandidateCard candidate={uploadedCV} />
            </div>
          )}
        </TabsContent>

        <TabsContent value="search" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Search & Filter Candidates</CardTitle>
              <CardDescription>Use semantic search and filters to find the perfect candidates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder="Search by name or skills..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Select value={locationFilter} onValueChange={setLocationFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by location" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Locations</SelectItem>
                      <SelectItem value="Ho Chi Minh City">Ho Chi Minh City</SelectItem>
                      <SelectItem value="London">London</SelectItem>
                      <SelectItem value="New York">New York</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="skill">Skills</Label>
                  <Select value={skillFilter} onValueChange={setSkillFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by skill" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Skills</SelectItem>
                      <SelectItem value="Python">Python</SelectItem>
                      <SelectItem value="JavaScript">JavaScript</SelectItem>
                      <SelectItem value="React">React</SelectItem>
                      <SelectItem value="Machine Learning">Machine Learning</SelectItem>
                      <SelectItem value="SQL">SQL</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold">Candidates ({filteredCandidates.length})</h3>
              <Button
                variant="outline"
                onClick={() => {
                  setSearchQuery("")
                  setLocationFilter("")
                  setSkillFilter("")
                }}
                className="border-green-300 text-green-700 hover:bg-green-50 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-950"
              >
                Clear Filters
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredCandidates.map((candidate) => (
                <CandidateCard key={candidate.id} candidate={candidate} />
              ))}
            </div>

            {filteredCandidates.length === 0 && (
              <Card>
                <CardContent className="text-center py-12">
                  <Search className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">No candidates found</h3>
                  <p className="text-muted-foreground">Try adjusting your search criteria or filters</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
