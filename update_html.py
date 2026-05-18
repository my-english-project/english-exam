import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update submit-wrap HTML
html = html.replace(
'''      <div class="submit-wrap">
        <button class="btn btn-green" onclick="submitExam()">Submit Exam ✓</button>
        <p class="submit-note">Review all your answers before submitting.</p>
      </div>''',
'''      <div class="submit-wrap">
        <button class="btn btn-green btn-submit" onclick="submitExam()">Submit Exam ✓</button>
        <p class="submit-note">Review all your answers before submitting.</p>
        <div id="fallback-download-container" style="display:none; text-align:center; margin-top:1.5rem; padding: 1.2rem; border: 1.5px dashed var(--red); border-radius: var(--r); background: var(--red-light);">
          <p style="color:var(--red); font-size:.9rem; margin-bottom: .8rem; line-height: 1.4;"><strong>Network Issue?</strong><br>If you are unable to submit, download your exam as a backup file and send it to your teacher.</p>
          <a id="fallback-download-link" class="btn btn-red" style="text-decoration:none; display:inline-block; font-size:.85rem; padding:.5rem 1rem;">📥 Download Exam File</a>
        </div>
      </div>'''
)

# 2. Update syncSubmissionToSupabase Catch Block
html = html.replace(
'''        } catch (e) {
          console.error('Sync error:', e);
          dbStatus = 'error';
          dbMessage = e.message || JSON.stringify(e);
        }
      }

      // Log to TXT file via PHP
      let readableLogStr = '';
      try { readableLogStr = formatReadableLog(sub); } catch(err) { console.warn('Could not format readable log:', err); }

      try {
        await fetch('api_log.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            payload: payload,
            readable_log: readableLogStr,
            db_status: dbStatus,
            db_message: dbMessage
          })
        });
      } catch (logErr) {
        console.error('Failed to save log to txt:', logErr);
      }
    }''',
'''        } catch (e) {
          console.error('Sync error:', e);
          dbStatus = 'error';
          dbMessage = e.message || JSON.stringify(e);
          return false;
        }
      } else {
        return false;
      }

      // Log to TXT file via PHP
      let readableLogStr = '';
      try { readableLogStr = formatReadableLog(sub); } catch(err) { console.warn('Could not format readable log:', err); }

      try {
        await fetch('api_log.php', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            payload: payload,
            readable_log: readableLogStr,
            db_status: dbStatus,
            db_message: dbMessage
          })
        });
      } catch (logErr) {
        console.error('Failed to save log to txt:', logErr);
      }
      return true;
    }'''
)

# 3. Update submitExam function
html = html.replace(
'''      submissions.push(submission);
      saveSubmissions();
      
      if (window._sb) {
        await syncSubmissionToSupabase(submission);
      }

      clearActiveExamSession();
      showResults(submission);
      showScreen('screen-results');
    }''',
'''      const btn = document.querySelector('.btn-submit');
      const originalText = btn ? btn.innerHTML : 'Submit Exam ✓';
      
      // Attempt to save to Supabase FIRST
      let syncSuccess = false;
      if (window._sb) {
        if (btn) { btn.innerHTML = 'Sending...'; btn.disabled = true; }
        syncSuccess = await syncSubmissionToSupabase(submission);
      }

      if (window._sb && !syncSuccess) {
        if (btn) { btn.innerHTML = originalText; btn.disabled = false; }
        
        // Show download option
        const container = document.getElementById('fallback-download-container');
        if (container) container.style.display = 'block';
        
        const jsonStr = JSON.stringify(submission);
        const blob = new Blob([jsonStr], {type: "application/json"});
        const url = URL.createObjectURL(blob);
        const a = document.getElementById('fallback-download-link');
        if (a) {
          a.href = url;
          a.download = `Exam_${studentName.replace(/\s+/g, '_')}.json`;
        }

        await showModal('Connection Error', 'We could not save your exam. Please check your internet connection and try submitting again. You can also download a Backup File below and send it to your teacher.', 'alert');
        return; // Abort submission, let student try again
      }

      submissions.push(submission);
      saveSubmissions();
      clearActiveExamSession();
      showResults(submission);
      showScreen('screen-results');
    }'''
)

# 4. Update renderPanel empty string
html = html.replace(
'''      if (!submissions.length) { body.innerHTML = `<div class="no-students">No submissions yet. Students who complete the exam will appear here.</div>`; return; }''',
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

# 5. Update renderPanel button area
html = html.replace(
'''      let html = `<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem">
        <span style="font-size:.83rem;color:var(--muted)">${total} submission(s) &nbsp;·&nbsp; ${graded} graded · click a row to grade</span>
        <button class="btn btn-ghost" style="font-size:.8rem;padding:.45rem .9rem" onclick="renderPanel()">↺ Refresh</button>
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

# 6. Insert handleBackupUpload
html = html.replace(
'''      return log.trim();
    }
  </script>
</body>''',
'''      return log.trim();
    }

    function handleBackupUpload(event) {
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
    }
  </script>
</body>'''
)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
