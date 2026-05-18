import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace empty submissions UI
html = html.replace(
'''      if (!submissions.length) { 
        body.innerHTML = `<div style="display:flex;justify-content:flex-end;margin-bottom:1rem">
          <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem" onclick="recoverBackup()">♻️ Recover Backup</button>
        </div><div class="no-students">No submissions yet. Students who complete the exam will appear here.</div>`; 
        return; 
      }''',
'''      if (!submissions.length) { 
        body.innerHTML = `<div style="display:flex;justify-content:flex-end;margin-bottom:1rem">
          <label class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem;cursor:pointer;">
            ♻️ Upload Backup
            <input type="file" style="display:none" accept=".json,.txt" onchange="handleBackupUpload(event)">
          </label>
        </div><div class="no-students">No submissions yet. Students who complete the exam will appear here.</div>`; 
        return; 
      }'''
)

# Replace table actions UI
html = html.replace(
'''      let html = `<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem">
        <span style="font-size:.83rem;color:var(--muted)">${total} submission(s) &nbsp;·&nbsp; ${graded} graded · click a row to grade</span>
        <div>
          <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem;margin-right:.5rem" onclick="recoverBackup()">♻️ Recover Backup</button>
          <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem;margin-right:.5rem" onclick="window.open('exam_logs.txt', '_blank')">📄 View Logs</button>
          <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem" onclick="renderPanel()">↺ Refresh</button>
        </div>
      </div>`;''',
'''      let html = `<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem">
        <span style="font-size:.83rem;color:var(--muted)">${total} submission(s) &nbsp;·&nbsp; ${graded} graded · click a row to grade</span>
        <div>
          <label class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem;margin-right:.5rem;cursor:pointer;">
            ♻️ Upload Backup
            <input type="file" style="display:none" accept=".json,.txt" onchange="handleBackupUpload(event)">
          </label>
          <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem;margin-right:.5rem" onclick="window.open('exam_logs.txt', '_blank')">📄 View Logs</button>
          <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem" onclick="renderPanel()">↺ Refresh</button>
        </div>
      </div>`;'''
)

# Replace recoverBackup() with handleBackupUpload()
old_recover = '''    async function recoverBackup() {
      try {
        const res = await fetch('exam_backup.jsonl');
        if (!res.ok) throw new Error('No backup file found on server.');
        const text = await res.text();
        const lines = text.split('\\n').filter(l => l.trim().length > 0);
        let recoveredCount = 0;

        lines.forEach(line => {
          try {
            const parsed = JSON.parse(line);
            
            // Check if already exists
            const exists = submissions.find(s => 
              (s.email === parsed.student_email && s.date === parsed.exam_date) || 
              (s.db_id && parsed.id && s.db_id === parsed.id)
            );
            
            if (!exists) {
              const sub = {
                id: parsed.id || Date.now() + Math.random(),
                name: parsed.student_name,
                email: parsed.student_email,
                date: parsed.exam_date,
                answers: parsed.answers,
                selectedQuestions: parsed.selected_questions,
                scores: parsed.scores,
                openPending: parsed.open_pending,
                graded: parsed.graded,
                emailSent: parsed.email_sent,
                db_id: parsed.id
              };
              submissions.push(sub);
              recoveredCount++;
            }
          } catch(e) {}
        });

        if (recoveredCount > 0) {
          saveSubmissions();
          renderPanel();
          showModal('Recovery Successful', `${recoveredCount} exam(s) were successfully recovered from backup and added to the panel.`, 'alert');
        } else {
          showModal('Recovery', 'All backup exams are already loaded in the panel. No new exams to recover.', 'alert');
        }
      } catch (err) {
        showModal('Error', 'Could not read backup file: ' + err.message, 'alert');
      }
    }'''

new_upload = '''    function handleBackupUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        try {
          const text = e.target.result;
          let parsed;
          try {
            parsed = JSON.parse(text);
          } catch(err) {
            throw new Error("Invalid file format. Please upload a valid JSON backup file generated by the exam.");
          }
          
          let recoveredCount = 0;
          const items = Array.isArray(parsed) ? parsed : [parsed];
          
          items.forEach(item => {
            const id = item.id || item.db_id;
            const email = item.email || item.student_email;
            const date = item.date || item.exam_date;
            
            const exists = submissions.find(s => 
              (s.email === email && s.date === date) || 
              (s.id === id || s.db_id === id)
            );
            
            if (!exists) {
              const sub = {
                id: id || Date.now() + Math.random(),
                name: item.name || item.student_name,
                email: email,
                date: date,
                answers: item.answers,
                selectedQuestions: item.selectedQuestions || item.selected_questions,
                scores: item.scores,
                openPending: item.openPending || item.open_pending,
                graded: item.graded || false,
                emailSent: item.emailSent || item.email_sent || false,
                db_id: item.db_id || item.id
              };
              submissions.push(sub);
              recoveredCount++;
            }
          });

          if (recoveredCount > 0) {
            saveSubmissions();
            renderPanel();
            showModal('Recovery Successful', `${recoveredCount} exam(s) were successfully recovered and added to the panel.`, 'alert');
          } else {
            showModal('Recovery', 'All uploaded exams are already loaded in the panel. No new exams to recover.', 'alert');
          }
        } catch (err) {
          showModal('Error', err.message, 'alert');
        }
        event.target.value = ''; // reset input
      };
      reader.readAsText(file);
    }'''

html = html.replace(old_recover, new_upload)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
