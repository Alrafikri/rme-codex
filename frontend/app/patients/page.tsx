'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '../../lib/api';

interface Patient {
  id: string;
  full_name: string;
  mrn: string;
  nik?: string;
  bpjs?: string;
}

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [form, setForm] = useState({
    full_name: '',
    mrn: '',
    nik: '',
    bpjs: '',
  });
  const [search, setSearch] = useState('');

  const load = async (q: string = '') => {
    const res = await apiFetch(`/api/patients/?search=${encodeURIComponent(q)}`);
    if (res.ok) {
      const data = await res.json();
      setPatients(data.results || data);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await apiFetch('/api/patients/', {
      method: 'POST',
      body: JSON.stringify(form),
    });
    if (res.ok) {
      setForm({ full_name: '', mrn: '', nik: '', bpjs: '' });
      load();
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <form onSubmit={submit} className="space-y-2">
        <input
          className="w-full p-2 border rounded"
          placeholder="Full name"
          value={form.full_name}
          onChange={(e) => setForm({ ...form, full_name: e.target.value })}
        />
        <input
          className="w-full p-2 border rounded"
          placeholder="MRN"
          value={form.mrn}
          onChange={(e) => setForm({ ...form, mrn: e.target.value })}
        />
        <input
          className="w-full p-2 border rounded"
          placeholder="NIK"
          value={form.nik}
          onChange={(e) => setForm({ ...form, nik: e.target.value })}
        />
        <input
          className="w-full p-2 border rounded"
          placeholder="BPJS"
          value={form.bpjs}
          onChange={(e) => setForm({ ...form, bpjs: e.target.value })}
        />
        <button className="w-full bg-blue-600 text-white p-2 rounded" type="submit">
          Save
        </button>
      </form>
      <div className="mt-4">
        <input
          className="w-full p-2 border rounded"
          placeholder="Search"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            load(e.target.value);
          }}
        />
        <ul className="mt-4 space-y-1">
          {patients.map((p) => (
            <li key={p.id} className="border p-2 rounded">
              <div className="font-semibold">{p.full_name}</div>
              <div className="text-sm">MRN: {p.mrn}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
