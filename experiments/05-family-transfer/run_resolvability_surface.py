"""Formal Gate B surface. HARD-DISABLED pending separate authorization."""
RESOLVABILITY_SURFACE_AUTHORIZED = False

def main():
    if not RESOLVABILITY_SURFACE_AUTHORIZED:
        raise SystemExit("STOP: resolvability surface is not authorized")
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--resume',action='store_true',help='Resume verified checkpoints under the same execution identity')
    args=parser.parse_args()
    from resolvability_runtime import phase_run
    phase_run('surface',__file__,resume=args.resume)

if __name__=='__main__':main()
