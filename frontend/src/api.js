// GET and POST api functions

export async function listDonations() {
    const res = await fetch('/api/donations')
    if (!res.ok) throw new Error('Failed to list donations')
    return res.json()
  }
  
  export async function createDonation(payload) {
    const res = await fetch('/api/donations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error('Failed to create donation')
    return res.json()
  }
  
  export async function updateDonation(id, payload) {
    const res = await fetch(`/api/donations/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) throw new Error('Failed to update donation')
    return res.json()
  }
  
  export async function deleteDonation(id) {
    const res = await fetch(`/api/donations/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete donation')
  }
  