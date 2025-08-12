import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Page, Navigation, TopBar, Frame } from '@shopify/polaris'
import {
  HomeMinor,
  AnalyticsMinor,
  ProductsMinor,
  SettingsMinor
} from '@shopify/polaris-icons'

import Dashboard from './components/Dashboard'
import ExperimentsList from './components/ExperimentsList'
import ExperimentDetails from './components/ExperimentDetails'
import CreateExperiment from './components/CreateExperiment'

const App: React.FC = () => {
  const [mobileNavigationActive, setMobileNavigationActive] = React.useState(false)

  const toggleMobileNavigationActive = React.useCallback(
    () =>
      setMobileNavigationActive(
        (mobileNavigationActive) => !mobileNavigationActive,
      ),
    [],
  )

  const navigationMarkup = (
    <Navigation location="/">
      <Navigation.Section
        items={[
          {
            url: '/',
            label: 'Dashboard',
            icon: HomeMinor,
          },
          {
            url: '/experiments',
            label: 'Experiments',
            icon: AnalyticsMinor,
          },
          {
            url: '/create',
            label: 'Create Experiment',
            icon: ProductsMinor,
          },
        ]}
      />
    </Navigation>
  )

  const topBarMarkup = (
    <TopBar
      showNavigationToggle
      onNavigationToggle={toggleMobileNavigationActive}
    />
  )

  return (
    <Router>
      <Frame
        topBar={topBarMarkup}
        navigation={navigationMarkup}
        showMobileNavigation={mobileNavigationActive}
        onNavigationDismiss={toggleMobileNavigationActive}
      >
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/experiments" element={<ExperimentsList />} />
          <Route path="/experiments/:id" element={<ExperimentDetails />} />
          <Route path="/create" element={<CreateExperiment />} />
        </Routes>
      </Frame>
    </Router>
  )
}

export default App
