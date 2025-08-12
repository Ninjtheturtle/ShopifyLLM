import React, { useState, useEffect } from 'react'
import {
  Page,
  Layout,
  Card,
  DisplayText,
  TextStyle,
  Badge,
  DataTable,
  Button,
  Stack,
  Spinner
} from '@shopify/polaris'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../services/api'

interface DashboardStats {
  total_experiments: number
  active_experiments: number
  completed_experiments: number
  total_conversions: number
  total_revenue: number
}

interface RecentExperiment {
  id: string
  name: string
  status: string
  experiment_type: string
  created_at: string
  variant_count: number
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [recentExperiments, setRecentExperiments] = useState<RecentExperiment[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load recent experiments
      const experimentsResponse = await api.get('/experiments?per_page=5')
      setRecentExperiments(experimentsResponse.data.experiments)

      // Calculate stats from experiments data
      const allExperimentsResponse = await api.get('/experiments?per_page=100')
      const experiments = allExperimentsResponse.data.experiments

      const dashboardStats: DashboardStats = {
        total_experiments: experiments.length,
        active_experiments: experiments.filter((exp: any) => exp.status === 'running').length,
        completed_experiments: experiments.filter((exp: any) => exp.status === 'completed').length,
        total_conversions: 0, // Would come from events API
        total_revenue: 0 // Would come from events API
      }

      setStats(dashboardStats)
    } catch (err) {
      console.error('Error loading dashboard data:', err)
      setError('Failed to load dashboard data')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge status="info">Running</Badge>
      case 'completed':
        return <Badge status="success">Completed</Badge>
      case 'stopped':
        return <Badge status="warning">Stopped</Badge>
      case 'draft':
        return <Badge>Draft</Badge>
      default:
        return <Badge>{status}</Badge>
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const experimentRows = recentExperiments.map((experiment) => [
    experiment.name,
    experiment.experiment_type,
    getStatusBadge(experiment.status),
    experiment.variant_count,
    formatDate(experiment.created_at),
    <Button url={`/experiments/${experiment.id}`} plain>View</Button>
  ])

  if (loading) {
    return (
      <Page title="Dashboard">
        <Layout>
          <Layout.Section>
            <Card sectioned>
              <Stack alignment="center">
                <Spinner size="large" />
                <TextStyle variation="subdued">Loading dashboard...</TextStyle>
              </Stack>
            </Card>
          </Layout.Section>
        </Layout>
      </Page>
    )
  }

  if (error) {
    return (
      <Page title="Dashboard">
        <Layout>
          <Layout.Section>
            <Card sectioned>
              <Stack alignment="center">
                <TextStyle variation="negative">{error}</TextStyle>
                <Button onClick={loadDashboardData}>Retry</Button>
              </Stack>
            </Card>
          </Layout.Section>
        </Layout>
      </Page>
    )
  }

  return (
    <Page
      title="A/B Testing Dashboard"
      subtitle="Monitor your experiments and performance"
      primaryAction={{
        content: 'Create Experiment',
        url: '/create'
      }}
    >
      <Layout>
        {/* Stats Cards */}
        <Layout.Section>
          <Layout>
            <Layout.Section oneThird>
              <Card>
                <Card.Section>
                  <Stack vertical spacing="tight">
                    <TextStyle variation="subdued">Total Experiments</TextStyle>
                    <DisplayText size="medium">
                      {stats?.total_experiments || 0}
                    </DisplayText>
                  </Stack>
                </Card.Section>
              </Card>
            </Layout.Section>

            <Layout.Section oneThird>
              <Card>
                <Card.Section>
                  <Stack vertical spacing="tight">
                    <TextStyle variation="subdued">Active Experiments</TextStyle>
                    <DisplayText size="medium" element="span">
                      <TextStyle variation="positive">
                        {stats?.active_experiments || 0}
                      </TextStyle>
                    </DisplayText>
                  </Stack>
                </Card.Section>
              </Card>
            </Layout.Section>

            <Layout.Section oneThird>
              <Card>
                <Card.Section>
                  <Stack vertical spacing="tight">
                    <TextStyle variation="subdued">Completed</TextStyle>
                    <DisplayText size="medium">
                      {stats?.completed_experiments || 0}
                    </DisplayText>
                  </Stack>
                </Card.Section>
              </Card>
            </Layout.Section>
          </Layout>
        </Layout.Section>

        {/* Recent Experiments Table */}
        <Layout.Section>
          <Card>
            <Card.Header>
              <Stack distribution="equalSpacing" alignment="center">
                <DisplayText size="small">Recent Experiments</DisplayText>
                <Button url="/experiments" plain>View all</Button>
              </Stack>
            </Card.Header>
            
            {recentExperiments.length > 0 ? (
              <DataTable
                columnContentTypes={[
                  'text',
                  'text', 
                  'text',
                  'numeric',
                  'text',
                  'text'
                ]}
                headings={[
                  'Name',
                  'Type',
                  'Status',
                  'Variants',
                  'Created',
                  'Action'
                ]}
                rows={experimentRows}
              />
            ) : (
              <Card.Section>
                <Stack alignment="center">
                  <TextStyle variation="subdued">
                    No experiments found. Create your first experiment to get started.
                  </TextStyle>
                  <Button primary url="/create">Create Experiment</Button>
                </Stack>
              </Card.Section>
            )}
          </Card>
        </Layout.Section>

        {/* Performance Chart Placeholder */}
        <Layout.Section>
          <Card>
            <Card.Header>
              <DisplayText size="small">Performance Overview</DisplayText>
            </Card.Header>
            <Card.Section>
              <div style={{ height: '300px', width: '100%' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={[
                      { name: 'Mon', conversions: 24 },
                      { name: 'Tue', conversions: 13 },
                      { name: 'Wed', conversions: 98 },
                      { name: 'Thu', conversions: 39 },
                      { name: 'Fri', conversions: 48 },
                      { name: 'Sat', conversions: 38 },
                      { name: 'Sun', conversions: 43 },
                    ]}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="conversions" stroke="#008060" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card.Section>
          </Card>
        </Layout.Section>
      </Layout>
    </Page>
  )
}

export default Dashboard
