"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Upload,
  Search,
  MapPin,
  Mail,
  Phone,
  Calendar,
  User,
  FileText,
  Moon,
  Sun,
  ExternalLink,
  Check,
  Laptop,
} from "lucide-react"
import { useTheme } from "next-themes"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import axios from "axios"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog"

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

const EDUCATION_LEVELS = [
  "High School",
  "Associate Degree",
  "Bachelor's Degree",
  "Master's Degree",
  "PhD",
  "Other"
]

function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          size="icon"
          className="border-green-200 hover:bg-green-50 hover:border-green-300 dark:border-green-800 dark:hover:bg-green-950"
        >
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          onClick={() => setTheme("light")}
          className={theme === "light" ? "bg-green-50 dark:bg-green-900" : ""}
        >
          <Sun className="mr-2 h-4 w-4" />
          <span>Light</span>
          {theme === "light" && <Check className="ml-auto h-4 w-4 text-green-600" />}
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme("dark")}
          className={theme === "dark" ? "bg-green-50 dark:bg-green-900" : ""}
        >
          <Moon className="mr-2 h-4 w-4" />
          <span>Dark</span>
          {theme === "dark" && <Check className="ml-auto h-4 w-4 text-green-600" />}
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setTheme("system")}
          className={theme === "system" ? "bg-green-50 dark:bg-green-900" : ""}
        >
          <Laptop className="mr-2 h-4 w-4" />
          <span>System</span>
          {theme === "system" && <Check className="ml-auto h-4 w-4 text-green-600" />}
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

export default function CVDashboard() {
  const [uploadedCV, setUploadedCV] = useState<Candidate | null>(null)
  const [formSearchQuery, setFormSearchQuery] = useState("")
  const [formLocationFilter, setFormLocationFilter] = useState("")
  const [formSkillFilter, setFormSkillFilter] = useState("")
  const [formMinExperience, setFormMinExperience] = useState("")
  const [formEducationLevel, setFormEducationLevel] = useState("")

  const [searchQuery, setSearchQuery] = useState<string>("")
  const [locationFilter, setLocationFilter] = useState("")
  const [skillFilter, setSkillFilter] = useState("")
  const [minExperience, setMinExperience] = useState("")
  const [educationLevel, setEducationLevel] = useState("")
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [skills, setSkills] = useState<string[]>([])
  const [locations, setLocations] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [semanticDetails, setSemanticDetails] = useState<any[]>([])
  const [showSemanticDetails, setShowSemanticDetails] = useState(false)
  
  const API_BASE_URL = "http://localhost:8000"
  // Fetch skills and locations for filters
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/v1/search/skills`).then(res => setSkills(res.data)).catch(() => setSkills([]))
    axios.get(`${API_BASE_URL}/api/v1/search/locations`).then(res => setLocations(res.data)).catch(() => setLocations([]))
  }, [])

  // Fetch candidates (only when search/filter state changes)
  useEffect(() => {
    setLoading(true)
    // If any filter/search is set, use semantic search endpoint
    if (
      searchQuery ||
      minExperience ||
      (skillFilter && skillFilter !== "all") ||
      (locationFilter && locationFilter !== "all") ||
      (educationLevel && educationLevel !== "all")
    ) {
      axios.get(`${API_BASE_URL}/api/v1/search/semantic`, {
        params: {
          ...(searchQuery ? { query: String(searchQuery) } : {}),
          min_experience_years: minExperience || undefined,
          required_skills: skillFilter && skillFilter !== "all" ? [skillFilter] : undefined,
          location: locationFilter && locationFilter !== "all" ? locationFilter : undefined,
          education_level: educationLevel && educationLevel !== "all" ? educationLevel : undefined,
          limit: 10,
          offset: 0,
        },
        paramsSerializer: params => {
    const usp = new URLSearchParams()
    Object.entries(params).forEach(([key, val]) => {
      if (Array.isArray(val)) {
        val.forEach(v => usp.append(key, v))
      } else if (val !== undefined) {
        usp.append(key, val)
      }
    })
    return usp.toString().replace(/\+/g, '%20')
  }
      })
        .then(res => setCandidates(res.data))
        .catch(() => setCandidates([]))
        .finally(() => setLoading(false))
    } else {
      // No filters: get all candidates
      axios.get(`${API_BASE_URL}/api/v1/candidates`, { params: { limit: 10, skip: 0 } })
        .then(res => setCandidates(res.data))
        .catch(() => setCandidates([]))
        .finally(() => setLoading(false))
    }
  }, [searchQuery, minExperience, skillFilter, locationFilter, educationLevel])

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const formData = new FormData()
      formData.append("file", file)
      try {
        const res = await axios.post(`${API_BASE_URL}/api/v1/cv/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        setUploadedCV(res.data)
      } catch (err) {
        setUploadedCV(null)
        alert("Failed to upload and process CV.")
      }
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

  // Handler for Search button
  const handleSearch = () => {
    setShowSemanticDetails(false)
    setSearchQuery(formSearchQuery)
    setLocationFilter(formLocationFilter)
    setSkillFilter(formSkillFilter)
    setMinExperience(formMinExperience)
    setEducationLevel(formEducationLevel)
  }

  // Handler for Semantic Detail Search button
  const handleSemanticDetailSearch = () => {
    setShowSemanticDetails(true)
    setLoading(true)
    axios.get(`${API_BASE_URL}/api/v1/search/semantic`, {
      params: {
        ...(formSearchQuery ? { query: String(formSearchQuery) } : {}),
        min_experience_years: formMinExperience || undefined,
        required_skills: formSkillFilter && formSkillFilter !== "all" ? [formSkillFilter] : undefined,
        location: formLocationFilter && formLocationFilter !== "all" ? formLocationFilter : undefined,
        education_level: formEducationLevel && formEducationLevel !== "all" ? formEducationLevel : undefined,
        limit: 10,
        offset: 0,
      },
      paramsSerializer: params => {
        const usp = new URLSearchParams()
        Object.entries(params).forEach(([key, val]) => {
          if (Array.isArray(val)) {
            val.forEach(v => usp.append(key, v))
          } else if (val !== undefined) {
            usp.append(key, val)
          }
        })
        return usp.toString().replace(/\+/g, '%20')
      }
    })
      .then(res => setSemanticDetails(res.data))
      .catch(() => setSemanticDetails([]))
      .finally(() => setLoading(false))
  }

  // Handler for Clear Filters button
  const handleClearFilters = () => {
    setFormSearchQuery("")
    setFormLocationFilter("")
    setFormSkillFilter("")
    setFormMinExperience("")
    setFormEducationLevel("")
    setSearchQuery("")
    setLocationFilter("")
    setSkillFilter("")
    setMinExperience("")
    setEducationLevel("")
  }

  // Handler for Filter button (calls /api/v1/search/filter)
  const handleFilter = async () => {
    setLoading(true)
    setShowSemanticDetails(false)
    try {
      const res = await axios.get(`${API_BASE_URL}/api/v1/search/filter`, {
        params: {
          min_experience_years: formMinExperience || undefined,
          required_skills: formSkillFilter && formSkillFilter !== "all" ? [formSkillFilter] : undefined,
          location: formLocationFilter && formLocationFilter !== "all" ? formLocationFilter : undefined,
          education_level: formEducationLevel && formEducationLevel !== "all" ? formEducationLevel : undefined,
          limit: 10,
          offset: 0,
        },
        paramsSerializer: params => {
          const usp = new URLSearchParams()
          Object.entries(params).forEach(([key, val]) => {
            if (Array.isArray(val)) {
              val.forEach(v => usp.append(key, v))
            } else if (val !== undefined) {
              usp.append(key, val)
            }
          })
          return usp.toString().replace(/\+/g, '%20')
        }
      })
      setCandidates(res.data)
    } catch (err) {
      setCandidates([])
      alert("Failed to filter candidates.")
    } finally {
      setLoading(false)
    }
  }

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
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Search</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder="Search by name, skills, etc..."
                      value={formSearchQuery}
                      onChange={(e) => setFormSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="min-experience">Min Experience (years)</Label>
                  <Input
                    id="min-experience"
                    type="number"
                    min={0}
                    placeholder="e.g. 2"
                    value={formMinExperience}
                    onChange={e => setFormMinExperience(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="skills">Skills</Label>
                  <Select value={formSkillFilter} onValueChange={setFormSkillFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by skill" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Skills</SelectItem>
                      {skills.map((skill) => (
                        <SelectItem key={skill} value={skill}>{skill}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Select value={formLocationFilter} onValueChange={setFormLocationFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by location" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Locations</SelectItem>
                      {locations.map((loc) => (
                        <SelectItem key={loc} value={loc}>{loc}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="education">Education Level</Label>
                  <Select value={formEducationLevel} onValueChange={setFormEducationLevel}>
                    <SelectTrigger>
                      <SelectValue placeholder="Filter by education" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Levels</SelectItem>
                      {EDUCATION_LEVELS.map((level) => (
                        <SelectItem key={level} value={level}>{level}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex gap-4 mt-4">
                <Button onClick={handleSearch} className="bg-green-600 hover:bg-green-700 text-white">Search</Button>
                <Button
                  variant="outline"
                  onClick={handleClearFilters}
                  className="border-green-300 text-green-700 hover:bg-green-50 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-950"
                >
                  Clear Filters
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleSemanticDetailSearch}
                  className="border-green-300 text-green-700 hover:bg-green-50 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-950"
                >
                  Semantic Detail Search
                </Button>
                <Button
                  variant="secondary"
                  onClick={handleFilter}
                  className="border-green-300 text-green-700 hover:bg-green-50 dark:border-green-700 dark:text-green-300 dark:hover:bg-green-950"
                >
                  Filter
                </Button>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-semibold">Candidates ({filteredCandidates.length})</h3>
            </div>

            {loading ? (
              <div className="text-center py-12">Loading candidates...</div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filteredCandidates.map((candidate) => (
                  <CandidateCard key={candidate.id} candidate={candidate} />
                ))}
              </div>
            )}

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

      {/* Semantic Details Modal */}
      <Dialog open={showSemanticDetails} onOpenChange={setShowSemanticDetails}>
        <DialogContent className="max-w-3xl w-full max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Semantic Search Details ({semanticDetails.length})</DialogTitle>
            <DialogDescription>
              These are the full details returned from the semantic search API.
            </DialogDescription>
          </DialogHeader>
          {loading ? (
            <div className="text-center py-12">Loading details...</div>
          ) : (
            semanticDetails.length === 0 ? (
              <div className="text-center text-muted-foreground">No detailed results found.</div>
            ) : (
              <div className="space-y-6">
                {semanticDetails.map((detail: any, idx: number) => (
                  <div key={idx} className="border rounded-lg p-4 bg-muted/10">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 mb-2">
                      <div>
                        <div className="text-lg font-bold flex items-center gap-2">
                          {detail.full_name}
                          <span className="text-xs text-muted-foreground">#{detail.id}</span>
                        </div>
                        <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mt-1">
                          <span>{detail.email}</span>
                          <span>{detail.phone}</span>
                          <span>{detail.location}</span>
                        </div>
                      </div>
                      <a
                        href={`https://drive.google.com/file/d/${detail.cv_file_id}/view`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-700 dark:text-green-300 underline text-sm font-medium"
                      >
                        View CV
                      </a>
                    </div>
                    {/* Skills */}
                    {detail.skills && detail.skills.length > 0 && (
                      <div className="mb-2">
                        <div className="font-semibold text-sm mb-1">Skills</div>
                        <div className="flex flex-wrap gap-2">
                          {detail.skills.map((skill: any, i: number) => (
                            <span key={i} className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 px-2 py-1 rounded text-xs">
                              {skill.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {/* Education */}
                    {detail.education && detail.education.length > 0 && (
                      <div className="mb-2">
                        <div className="font-semibold text-sm mb-1">Education</div>
                        <ul className="list-disc pl-5 space-y-1">
                          {detail.education.map((edu: any, i: number) => (
                            <li key={i}>
                              <div className="font-medium">{edu.degree} - {edu.institution}</div>
                              <div className="text-xs text-muted-foreground">
                                {edu.field_of_study}
                                {edu.start_date && (
                                  <> | {new Date(edu.start_date).toLocaleDateString()} - {edu.end_date ? new Date(edu.end_date).toLocaleDateString() : 'Present'}</>
                                )}
                              </div>
                              {edu.description && <div className="text-xs mt-1">{edu.description}</div>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {/* Work Experience */}
                    {detail.work_experience && detail.work_experience.length > 0 && (
                      <div className="mb-2">
                        <div className="font-semibold text-sm mb-1">Work Experience</div>
                        <ul className="list-disc pl-5 space-y-1">
                          {detail.work_experience.map((work: any, i: number) => (
                            <li key={i}>
                              <div className="font-medium">{work.position} - {work.company}</div>
                              <div className="text-xs text-muted-foreground">
                                {work.location && <>{work.location} | </>}
                                {work.start_date && (
                                  <>{new Date(work.start_date).toLocaleDateString()} - {work.end_date ? new Date(work.end_date).toLocaleDateString() : 'Present'}</>
                                )}
                              </div>
                              {work.description && <div className="text-xs mt-1">{work.description}</div>}
                              {work.achievements && <div className="text-xs mt-1">Achievements: {work.achievements}</div>}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {/* Certifications */}
                    {detail.certifications && detail.certifications.length > 0 && (
                      <div className="mb-2">
                        <div className="font-semibold text-sm mb-1">Certifications</div>
                        <ul className="list-disc pl-5 space-y-1">
                          {detail.certifications.map((cert: any, i: number) => (
                            <li key={i}>
                              <div className="font-medium">{cert.name}</div>
                              <div className="text-xs text-muted-foreground">
                                {cert.issuer && <>{cert.issuer} | </>}
                                {cert.issue_date && <>Issued: {new Date(cert.issue_date).toLocaleDateString()}</>}
                                {cert.expiry_date && <> | Expires: {new Date(cert.expiry_date).toLocaleDateString()}</>}
                              </div>
                              {cert.credential_url && (
                                <a href={cert.credential_url} target="_blank" rel="noopener noreferrer" className="text-xs underline text-green-700 dark:text-green-300">Credential</a>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {/* Projects */}
                    {detail.projects && detail.projects.length > 0 && (
                      <div className="mb-2">
                        <div className="font-semibold text-sm mb-1">Projects</div>
                        <ul className="list-disc pl-5 space-y-1">
                          {detail.projects.map((proj: any, i: number) => (
                            <li key={i}>
                              <div className="font-medium">{proj.name}</div>
                              {proj.description && <div className="text-xs mt-1">{proj.description}</div>}
                              {proj.technologies && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {Array.isArray(proj.technologies)
                                    ? proj.technologies.map((tech: string, j: number) => (
                                        <span key={j} className="bg-gray-200 dark:bg-gray-800 px-2 py-0.5 rounded text-xs">{tech}</span>
                                      ))
                                    : <span className="bg-gray-200 dark:bg-gray-800 px-2 py-0.5 rounded text-xs">{proj.technologies}</span>
                                  }
                                </div>
                              )}
                              {proj.url && (
                                <a href={proj.url} target="_blank" rel="noopener noreferrer" className="text-xs underline text-green-700 dark:text-green-300">Project Link</a>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
