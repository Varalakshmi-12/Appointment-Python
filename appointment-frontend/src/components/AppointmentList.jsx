import { useEffect, useState } from "react";
import API from "../api";
import { Link } from "react-router-dom";

export default function AppointmentList() {
  const [appointments, setAppointments] = useState([]);

  useEffect(() => {
    API.get("/appointments").then((res) => setAppointments(res.data));
  }, []);

  return (
    <div>
      <h2>List Of Appointments</h2>
      <table>
        <thead>
          <tr>
            <th>Patient Name</th>
            <th>Phone</th>
            <th>Provider</th>
            <th>Email</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {appointments.map((a) => (
            <tr key={a.id}>
              <td>{a.patient_name}</td>
              <td>{a.patient_phone}</td>
              <td>{a.provider_name}</td>
              <td>{a.patient_email}</td>
              <td>{a.appointment_time}</td>
              <td>
                <Link to={`/edit/${a.id}`}>Edit</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
        
        
      <Link to="/new" style={{ marginLeft: "10px" }}>
        New Appointment
          </Link>
    </div>
    
  );
}