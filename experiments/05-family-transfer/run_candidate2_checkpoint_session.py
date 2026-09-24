"""Bounded validation sessions. Uploads require a separate isolated authorization."""
CANDIDATE2_CHECKPOINT_UPLOAD_AUTHORIZED = False

def main():
    if not CANDIDATE2_CHECKPOINT_UPLOAD_AUTHORIZED:
        raise SystemExit('STOP: production checkpoint uploads are not authorized')
    from candidate2_checkpoint_controller import launch
    launch(__file__)

if __name__=='__main__':main()
