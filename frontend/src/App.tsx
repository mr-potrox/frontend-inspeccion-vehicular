import React from 'react';
import { Layout } from './components/layout/Layout';
import { InspectionFlow } from './components/inspection/InspectionFlow';
import { InspectionProvider } from './contexts/InspectionContext';

function App() {
  return (
    <InspectionProvider>
      <Layout>
        <InspectionFlow />
      </Layout>
    </InspectionProvider>
  );
}

export default App;