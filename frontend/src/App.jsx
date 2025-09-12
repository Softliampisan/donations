import { useEffect, useState } from 'react'
import { listDonations, createDonation, updateDonation, deleteDonation } from './api'
import './App.css'

export default function App() {
  const [donations, setDonations] = useState([])
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState({
    donor_name: '',
    donation_type: 'money',
    quantity_or_amount: 1,
    date: new Date().toISOString().slice(0, 10),
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function refresh() {
    setLoading(true); setError(null)
    try {
      const data = await listDonations()
      setDonations(data)
    } catch (e) {
      setError(e.message || 'Failed to fetch')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])

  function startEdit(d) {
    setEditing(d)
    setForm({
      donor_name: d.donor_name,
      donation_type: d.donation_type,
      quantity_or_amount: d.quantity_or_amount,
      date: d.date,
    })
  }

  function cancelEdit() {
    setEditing(null)
    setForm({ donor_name: '', donation_type: 'money', quantity_or_amount: 1, date: new Date().toISOString().slice(0, 10) })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const payload = {
      donor_name: form.donor_name.trim(),
      donation_type: form.donation_type,
      quantity_or_amount: Number(form.quantity_or_amount),
      date: form.date,
    }
    if (editing) {
      await updateDonation(editing.id, payload)
    } else {
      await createDonation(payload)
    }
    cancelEdit()
    await refresh()
  }

  async function handleDelete(id) {
    await deleteDonation(id)
    await refresh()
  }

  return (
    <div className="page">
      <h1>Donation Inventory</h1>
      <div className="content">
        <div className="form">
          <form onSubmit={handleSubmit} className="donation-form">
            <fieldset>
              <legend>{editing ? `Edit Donation #${editing.id}` : 'Add Donation'}</legend>

              <label style={{ display: 'block', margin: '8px 0' }}>
                Donor name
                <input
                  value={form.donor_name}
                  onChange={(e) => setForm({ ...form, donor_name: e.target.value })}
                  required
                />
              </label>

              <label style={{ display: 'block', margin: '8px 0' }}>
                Donation type
                <select
                  value={form.donation_type}
                  onChange={(e) => setForm({ ...form, donation_type: e.target.value })}
                  required
                >
                  <option value="money">Money</option>
                  <option value="food">Food</option>
                  <option value="clothing">Clothing</option>
                  <option value="other">Other</option>
                </select>
              </label>

              <label style={{ display: 'block', margin: '8px 0' }}>
                Quantity / Amount
                <input
                  type="number" min="1" step="1"
                  value={form.quantity_or_amount}
                  onChange={(e) => setForm({ ...form, quantity_or_amount: e.target.value })}
                  required
                />
              </label>

              <label style={{ display: 'block', margin: '8px 0' }}>
                Date
                <input
                  type="date"
                  value={form.date}
                  onChange={(e) => setForm({ ...form, date: e.target.value })}
                  required
                />
              </label>

              <div style={{ marginTop: 10 }}>
                <button type="submit">{editing ? 'Update' : 'Save'}</button>
                {editing && <button type="button" onClick={cancelEdit} style={{ marginLeft: 8 }}>Cancel</button>}
              </div>
            </fieldset>
          </form>
        </div>

        {loading && <p>Loading…</p>}
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <div className="table-wrapper">
          <table className="donations-table">
            <thead>
              <tr>
                <th style={{ textAlign: 'left' }}>ID</th>
                <th style={{ textAlign: 'left' }}>Donor</th>
                <th style={{ textAlign: 'left' }}>Type</th>
                <th style={{ textAlign: 'left' }}>Qty/Amount</th>
                <th style={{ textAlign: 'left' }}>Date</th>
                <th style={{ textAlign: 'left' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {donations.map(row => (
                <tr key={row.id}>
                  <td>{row.id}</td>
                  <td>{row.donor_name}</td>
                  <td>{row.donation_type}</td>
                  <td>{row.quantity_or_amount}</td>
                  <td>{row.date}</td>
                  <td>
                    <button onClick={() => startEdit(row)}>Edit</button>
                    <button onClick={() => handleDelete(row.id)} style={{ marginLeft: 8 }}>Delete</button>
                  </td>
                </tr>
              ))}
              {donations.length === 0 && (
                <tr><td colSpan="6" style={{ color: '#777' }}>No donations yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
