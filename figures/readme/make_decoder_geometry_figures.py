
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8.5,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 200,
})

BIO = "#3730a3"
NUL = "#be123c"
CMA = "#b45309"
ISO = "#475569"
GREY = "#94a3b8"
LIGHT = "#e2e8f0"

OUT = Path(__file__).resolve().parent

K_GRID = [1,2,4,8,16,32,64,128,256,512]

ISO_MED = [0.011363,0.022776,0.042656,0.078125,0.139407,
           0.241249,0.400241,0.618333,0.850045,0.984837]
ISO_LO = [0.008679,0.017820,0.035491,0.068048,0.126110,
          0.224466,0.380195,0.597710,0.837652,0.981317]
ISO_HI = [0.017453,0.029606,0.052351,0.090720,0.156129,
          0.261673,0.422658,0.639764,0.863021,0.987128]

R32 = {
    "Biological": (0.25680454605778436,0.25437069970782267,0.2568052260279048),
    "Canonical null": (0.2566901081228934,0.2463111919820875,0.26862768200872467),
    "C-matched null": (0.2432864945440445,0.24102957499090782,0.24617142975517936),
    "Isotropic": (0.24124923558528533,0.24060283908885444,0.24209149900170346),
}

TOP32 = {
    "Biological": (0.028699009019077543,0.028698753922082376,0.02871144008219902),
    "Canonical null": (0.025300875054981853,0.023246661627686127,0.026061959124384013),
    "C-matched null": (0.026172597355208077,0.02576181977158953,0.026678135509173174),
    "Isotropic": (0.025439204432141968,0.025275390976861475,0.025571707284947977),
}

NEFF = {
    "Biological": (6373.671377221852,6373.661112910348,6373.686930528624),
    "Canonical null": (6473.911215623586,6419.639228881237,6760.980242562455),
    "C-matched null": (6393.910242959088,6384.870934044266,6409.638397705112),
    "Isotropic": (6451.580837751319,6443.149625559201,6460.771525497181),
}

DIFF = {
    "r32": {
        "bio - null": (0.00011443793489096521,-0.011823361349443309,0.010492731193718463),
        "bio - C-matched": (0.01351805151373986,0.010049027099860853,0.015596994982009612),
        "bio - isotropic": (0.015555310472499029,0.012999165465473536,0.016194963854089493),
        "null - C-matched": (0.013403613578848894,0.0033596083363507836,0.0253247069489396),
        "null - isotropic": (0.015440872537608064,0.0052664281255458125,0.0272102456973648),
        "C-matched - isotropic": (0.0020372589587591694,-0.00023903942752293833,0.005042621257670311),
    },
    "top32": {
        "bio - null": (0.00339813396409569,0.002637392230020987,0.0054520350668448665),
        "bio - C-matched": (0.0025264116638694656,0.002020652353325685,0.00291879950941399),
        "bio - isotropic": (0.0032598045869355746,0.0031300624360551233,0.00342700463917027),
        "null - C-matched": (-0.0008717223002262242,-0.002851039964321296,7.305462842518984e-05),
        "null - isotropic": (-0.00013832937716011517,-0.002023286695098632,0.0006212801782419125),
        "C-matched - isotropic": (0.000733392923066109,0.00028902447644744284,0.0012349896326139284),
    },
    "neff": {
        "bio - null": (-100.23983840173423,-377.89226637133726,-45.97359089187921),
        "bio - C-matched": (-20.238865737235756,-36.095386277854644,-11.193795321435779),
        "bio - isotropic": (-77.90946052946765,-87.03903421601804,-69.20111969537025),
        "null - C-matched": (80.00097266449848,24.53536253601669,360.2823726021551),
        "null - isotropic": (22.33037787226658,-30.687795070444736,305.0946379980004),
        "C-matched - isotropic": (-57.670594792231896,-71.32531928216227,-38.95389930861256),
    },
}

THRESH = {
    "Biological": {
        "n":100,
        0.50:{32:0,64:0,128:100,256:100,512:100},
        0.80:{32:0,64:0,128:0,256:100,512:100},
        0.90:{32:0,64:0,128:0,256:0,512:100},
    },
    "Canonical null": {
        "n":63,
        0.50:{32:7,64:11,128:63,256:63,512:63},
        0.80:{32:0,64:4,128:6,256:63,512:63},
        0.90:{32:0,64:0,128:4,256:9,512:63},
    },
    "C-matched null": {
        "n":100,
        0.50:{32:0,64:0,128:100,256:100,512:100},
        0.80:{32:0,64:0,128:0,256:100,512:100},
        0.90:{32:0,64:0,128:0,256:0,512:100},
    },
}

NORM_Q = [0.0,0.01,0.05,0.25,0.50,0.75,0.95,0.99,1.0]
NORM_V = [
    0.16518653135561567,11.623418791672556,16.692507738043695,
    39.79910648467381,70.37959376829666,101.60891968935921,
    147.84831595047172,225.8934957662065,413.5946889603151
]

SV_HEAD = [
    3324.804889494999,777.0675144927624,568.9925143143348,
    525.3704392006022,494.4621408927569,484.7225283267437,
    481.53506606934377,473.4324700338785,467.2193715162078,
    465.94799306707506
]

SV_TAIL = [
    90.49673382704344,88.42189957791896,87.73623407124661,
    84.63333491747031,80.19678289016449,77.66501125210331,
    75.28924676759613,72.24640560808548,52.33656915327834,
    19.627332446836256
]

def save(fig,name):
    fig.savefig(OUT/f"{name}.png",dpi=220,bbox_inches="tight",pad_inches=0.04)
    fig.savefig(OUT/f"{name}.pdf",bbox_inches="tight",pad_inches=0.04)
    plt.close(fig)
    print("wrote",name)

def fig1():
    fig,ax=plt.subplots(figsize=(9.2,3.4))
    ax.set_xlim(0,100); ax.set_ylim(0,42); ax.axis("off")

    def box(x,y,w,h,title,body,color):
        ax.add_patch(FancyBboxPatch(
            (x,y),w,h,boxstyle="round,pad=0.6,rounding_size=1.2",
            fc="white",ec=color,lw=1.0,zorder=3))
        ax.text(x+w/2,y+h-3,title,ha="center",va="top",
                fontsize=9,weight="bold",color=color)
        ax.text(x+w/2,y+h-8.4,body,ha="center",va="top",
                fontsize=7.4,color="#334155",linespacing=1.5)

    def arrow(x1,y1,x2,y2):
        ax.add_patch(FancyArrowPatch(
            (x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=9,
            lw=1,color="#94a3b8"))

    box(0.5,22,21,18,"Frozen inputs",
        "ESM-2 650M layer 18\n278 discovery proteins\nInterPLM SAE\n1280 × 10240","#0f766e")
    box(26,22,21,18,"Stage-B probe directions",
        "L1 logistic, N=139\n200 canonical fits\nbyte-verified replay",BIO)
    box(51.5,22,21,18,"Decoder geometry",
        "OMP, k grid 1…512\njoint LS refit\nw = Dᵀβ","#7c3aed")
    box(77,22,22.5,18,"Descriptive summary",
        "median R(32), top-32\nmass, N_eff\n10,000 bootstrap","#334155")

    arrow(22.6,31,25,31)
    arrow(48.1,31,50.5,31)
    arrow(73.6,31,76,31)

    pops=[
        ("Biological","100 / 100 eligible",BIO,0.5,22.0),
        ("Canonical null","63 / 100 eligible",NUL,25.5,22.0),
        ("C-matched null","100 / 100 eligible",CMA,50.5,22.0),
        ("Isotropic reference","1000 directions",ISO,75.5,24.0),
    ]

    for title,sub,col,x,w in pops:
        ax.add_patch(FancyBboxPatch(
            (x,2.5),w,12,boxstyle="round,pad=0.5,rounding_size=1",
            fc=col,ec="none",alpha=.10))
        ax.add_patch(Rectangle((x,2.5),.9,12,fc=col,ec="none"))
        ax.text(x+w/2+.5,10.5,title,ha="center",fontsize=8,weight="bold",color=col)
        ax.text(x+w/2+.5,5.5,sub,ha="center",fontsize=7,color="#475569")

    ax.text(50,18.5,"four frozen comparison populations",
            ha="center",fontsize=7.5,style="italic",color="#64748b")

    save(fig,"exp04_fig1_design")

def fig2():
    fig,axes=plt.subplots(1,2,figsize=(9.2,3.6),
                          gridspec_kw={"width_ratios":[1.25,1],"wspace":.32})

    ax=axes[0]
    x=np.arange(len(K_GRID))
    ax.fill_between(x,ISO_LO,ISO_HI,color=ISO,alpha=.16,lw=0)
    ax.plot(x,ISO_MED,"-o",color=ISO,ms=3,lw=1.2,label="isotropic median")

    for t,lo_k,hi_k in [(0.50,64,128),(0.80,128,256),(0.90,256,512)]:
        i0,i1=K_GRID.index(lo_k),K_GRID.index(hi_k)
        ax.add_patch(Rectangle((i0,t-.012),i1-i0,.024,fc=BIO,ec="none",alpha=.22))
        ax.text((i0+i1)/2,t+.03,f"R={t:.2f}",ha="center",
                fontsize=7,color=BIO,weight="bold")

    ax.plot([K_GRID.index(32)],[R32["Biological"][0]],"D",color=BIO,ms=6,label="biological")
    ax.plot([K_GRID.index(32)],[R32["C-matched null"][0]],"s",color=CMA,ms=5,label="C-matched")
    ax.plot([K_GRID.index(32)],[R32["Canonical null"][0]],"^",color=NUL,ms=5,label="canonical null")

    ax.axvline(K_GRID.index(32),color="#cbd5e1",lw=.7,ls=":")
    ax.set_xticks(x)
    ax.set_xticklabels(K_GRID)
    ax.set_xlabel("k — decoder atoms selected by OMP")
    ax.set_ylabel("R(k) — reconstructed fraction of ||β||²")
    ax.set_ylim(0,1.04)
    ax.legend(frameon=False,loc="upper left")
    ax.set_title("(a) Reconstruction versus sparsity",loc="left")

    ax=axes[1]
    names=["Biological","Canonical null","C-matched null","Isotropic"]
    cols=[BIO,NUL,CMA,ISO]
    ys=np.arange(len(names))[::-1]

    for y,n,c in zip(ys,names,cols):
        est,lo,hi=R32[n]
        ax.plot([lo,hi],[y,y],color=c,lw=2.4,alpha=.55)
        ax.plot(est,y,"o",color=c,ms=5)
        ax.text(hi+.0016,y,f"{est:.4f}",va="center",fontsize=7,color=c)

    ax.set_yticks(ys)
    ax.set_yticklabels(names)
    ax.set_xlabel("median R(32)")
    ax.set_xlim(.2375,.2755)
    ax.set_title("(b) Headline k = 32",loc="left")
    ax.grid(axis="x",color=LIGHT,lw=.5)

    save(fig,"exp04_fig2_reconstruction")

def fig3():
    order=[
        "bio - null","bio - C-matched","bio - isotropic",
        "null - C-matched","null - isotropic","C-matched - isotropic"
    ]

    titles=[
        ("r32","(a) median R(32) difference","difference"),
        ("top32","(b) median top-32 mass difference","difference"),
        ("neff","(c) median N_eff difference","difference (atoms)")
    ]

    fig,axes=plt.subplots(1,3,figsize=(9.2,3.4),
                          gridspec_kw={"wspace":.55})

    for ax,(key,title,xlab) in zip(axes,titles):
        ys=np.arange(len(order))[::-1]

        for y,name in zip(ys,order):
            est,lo,hi=DIFF[key][name]
            c=BIO if name.startswith("bio") else (
                NUL if name.startswith("null") else CMA
            )
            crosses=lo<0<hi
            ax.plot([lo,hi],[y,y],color=c,lw=2,alpha=.5)
            ax.plot(est,y,"o",color=c,ms=4,
                    mfc="white" if crosses else c,mew=1.1)

        ax.axvline(0,color="#475569",lw=.7,ls="--")
        ax.set_yticks(ys)
        ax.set_yticklabels(order if key=="r32" else [""]*len(order))
        ax.set_xlabel(xlab)
        ax.set_title(title,loc="left")
        ax.grid(axis="x",color=LIGHT,lw=.5)

    handles=[
        Line2D([],[],marker="o",color="#475569",mfc="#475569",
               ls="none",label="interval excludes 0"),
        Line2D([],[],marker="o",color="#475569",mfc="white",
               ls="none",label="interval includes 0")
    ]

    fig.legend(handles=handles,frameon=False,ncol=2,
               loc="lower center",bbox_to_anchor=(.5,-.08))

    save(fig,"exp04_fig3_differences")

def fig4():
    fig,axes=plt.subplots(1,4,figsize=(9.2,3.0),
                          gridspec_kw={"wspace":.28})
    ks=[32,64,128,256,512]

    for ax,(pop,col) in zip(
        axes[:3],
        [("Biological",BIO),("Canonical null",NUL),("C-matched null",CMA)]
    ):
        n=THRESH[pop]["n"]
        w=.26

        for j,t in enumerate([.50,.80,.90]):
            vals=[THRESH[pop][t][k]/n for k in ks]
            ax.bar(np.arange(len(ks))+(j-1)*w,vals,width=w,
                   color=col,alpha=.35+.3*j,ec=col,lw=.5,
                   label=f"R ≥ {t:.2f}")

        ax.set_xticks(np.arange(len(ks)))
        ax.set_xticklabels([f"≤{k}" for k in ks],rotation=45)
        ax.set_ylim(0,1.08)
        ax.set_title(f"{pop} (n={n})",loc="left")
        ax.grid(axis="y",color=LIGHT,lw=.5)

        if pop=="Biological":
            ax.set_ylabel("cumulative proportion")
            ax.legend(frameon=False,fontsize=6.5)
        else:
            ax.set_yticklabels([])

    ax=axes[3]
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.add_patch(Rectangle(
        (.06,.16),.88,.68,fc="none",ec=GREY,
        lw=.8,ls="--",hatch="///",alpha=.28
    ))

    ax.text(.5,.63,"Isotropic (n=1000)",ha="center",
            fontsize=8,weight="bold",color="#475569")
    ax.text(.5,.38,
            "threshold fields were\nnever serialized\n(1000/1000 unavailable)",
            ha="center",fontsize=7,color="#475569",linespacing=1.5)
    ax.axis("off")
    ax.set_title("no reference available",loc="left",color="#64748b")

    save(fig,"exp04_fig4_thresholds")

def fig5():
    fig,axes=plt.subplots(1,3,figsize=(9.2,3.2),
                          gridspec_kw={"wspace":.38})

    ax=axes[0]
    ax.plot(np.array(NORM_Q)*100,NORM_V,"-o",
            color="#7c3aed",ms=3,lw=1.2)
    ax.set_xlabel("quantile of decoder atoms (%)")

    # Portable fix:
    # use Matplotlib mathtext rather than Unicode script-small-l.
    ax.set_ylabel(r"column $\ell_2$ norm")

    ax.set_title("(a) Atom norms",loc="left")
    ax.grid(color=LIGHT,lw=.5)
    ax.text(3,350,"9 exact-zero atoms\nexcluded (10,231 used)",
            fontsize=7,color="#64748b")

    ax=axes[1]
    xh=np.arange(1,11)
    xt=np.arange(13,23)

    ax.plot(xh,SV_HEAD,"-o",color="#0f766e",ms=3,lw=1.2)
    ax.plot(xt,SV_TAIL,"-o",color="#0f766e",ms=3,lw=1.2)
    ax.axvline(11.5,color=GREY,lw=.7,ls=":")
    ax.text(11.5,2600,"  ...",fontsize=10,color=GREY,va="center")
    ax.set_xticks([1,5,10,13,18,22])
    ax.set_xticklabels(["1","5","10","1271","1276","1280"])
    ax.set_xlabel("singular value index")
    ax.set_ylabel("singular value")
    ax.set_title("(b) Decoder spectrum",loc="left")
    ax.grid(color=LIGHT,lw=.5)
    ax.text(3,1900,"rank 1280\ncond. 169.4\nentropy eff. rank 548",
            fontsize=7,color="#334155",linespacing=1.5)

    ax=axes[2]
    names=["Bio","Null","C-match","Iso"]
    keys=["Biological","Canonical null","C-matched null","Isotropic"]
    cols=[BIO,NUL,CMA,ISO]

    for i,(k,c) in enumerate(zip(keys,cols)):
        est,lo,hi=NEFF[k]
        ax.bar(i,est,width=.6,color=c,alpha=.75,ec=c,lw=.6)
        ax.plot([i,i],[lo,hi],color="#1e293b",lw=1.1)

    ax.axhline(10231,color="#0f766e",lw=.9,ls="--")
    ax.text(1.5,10650,"10,231 usable atoms",
            ha="center",fontsize=7,color="#0f766e")
    ax.set_xticks(range(4))
    ax.set_xticklabels(names)
    ax.set_ylim(0,12000)
    ax.set_ylabel("N_eff — effective atoms")
    ax.set_title("(c) Effective decoder support",loc="left")
    ax.grid(axis="y",color=LIGHT,lw=.5)

    save(fig,"exp04_fig5_decoder")

if __name__ == "__main__":
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    print("all five decoder-geometry figures generated")
