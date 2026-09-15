"""Collect verified generation, delivery, archive and owned-resource receipts."""
from collections import Counter
from run import lab

def main():
    work=lab.APP/'work/storytelling-session'
    checks=sorted((lab.OUT/'checks').glob('*generation.json'))
    jobs=[row for p in checks for row in lab.read(p)['jobs']]
    assert len(jobs)==len({r['prompt_id'] for r in jobs})==269
    deliveries=[]
    for p in sorted(lab.OUT.glob('*/faster/rife-moving-tail/manifest.json'))+[
        lab.OUT/'i5-the-open-dream/through-0684/rife-moving-tail/manifest.json']:
        m=lab.read(p);d=lab.read(p.parent.parent/'delivery-check.json')
        assert m['status']=='complete' and d['verified']
        assert lab.sha(p.parent/'preview.mp4')==m['video_sha256']
        assert m['settings']['output_fps']==24 and m['final_warps']==7 and m['final_holds']==0
        for row in m['output_frames']:
            assert lab.sha(p.parent/row['file'])==row['sha256']
        deliveries.append(dict(path=str((p.parent/'preview.mp4').relative_to(lab.APP)),
            video_sha256=m['video_sha256'],frames=len(m['output_frames']),
            paintings=len(m['settings']['anchor_frames']),fps=24,final_warps=7))
    assert len(deliveries)==14
    archive=lab.read(work/'final-archive-verification.json')
    assert archive['verified'] and archive['files']==4635
    remote=lab.read(work/'remote-cleanup.json');cloud=lab.read(work/'cloud-cleanup.json')
    assert remote['removed_remote_files']==535 and remote['queue_empty']
    assert cloud['delete_response']['status']==204 and cloud['pods_after']==[]
    before=lab.read(work/'account-start.json');after=lab.read(work/'account-end.json')
    result=dict(date='2026-09-16',work_window_utc=['2026-09-15T21:21:17Z','2026-09-15T22:51:17Z'],
        new_image_jobs=269,jobs_by_case=dict(Counter(r['case'] for r in jobs)),
        generation_checks=[str(p.relative_to(lab.APP)) for p in checks],
        archive=archive,deliveries=deliveries,
        posted_account_debit_at_cleanup=round(before['clientBalance']-after['clientBalance'],10),
        conservative_session_usd=1.0,conservative_cumulative_usd=5.4,budget_usd=10,
        account_spend_per_hour_after=after['currentSpendPerHr'],
        resources={**cloud,'removed_remote_media_files':535,'remote_scratch_removed':True},
        human_feedback='pending',review_scope='Chronological painting samples, selected full images, consecutive finishing ranges, independent plot-blind painting review')
    lab.save(lab.HERE/'execution-summary.json',result)
    print('Verified 269 jobs, 4635 archive entries and 14 complete 24 fps deliveries.')

if __name__=='__main__':main()
