'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '../../lib/api';

interface Ticket {
  id: string;
  number: number;
  state: string;
  patient_name: string;
}

export default function QueuePage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const load = async () => {
    const res = await apiFetch('/api/queue/');
    if (res.ok) {
      setTickets(await res.json());
    }
  };
  useEffect(() => {
    load();
  }, []);

  const callNext = async () => {
    const res = await apiFetch('/api/queue/next/', { method: 'POST' });
    if (res.ok) {
      await load();
    }
  };

  const act = async (id: string, action: 'done' | 'skip') => {
    const res = await apiFetch(`/api/queue/${id}/${action}/`, { method: 'POST' });
    if (res.ok) {
      await load();
    }
  };

  return (
    <div className="p-4 space-y-2">
      <button
        onClick={callNext}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        Call Next
      </button>
      <ul className="space-y-2">
        {tickets.map((t) => (
          <li key={t.id} className="border p-2 flex justify-between">
            <span>
              {t.number}. {t.patient_name} - {t.state}
            </span>
            {t.state === 'IN_PROGRESS' && (
              <span className="space-x-2">
                <button
                  onClick={() => act(t.id, 'done')}
                  className="bg-green-600 text-white px-2 py-1 rounded"
                >
                  Done
                </button>
                <button
                  onClick={() => act(t.id, 'skip')}
                  className="bg-yellow-600 text-white px-2 py-1 rounded"
                >
                  Skip
                </button>
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
