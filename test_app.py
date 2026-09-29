from streamlit.testing.v1 import AppTest
import bfup_ex2 as core


def test_course_values():
    r = core.ex2_compute()
    assert abs(r["A_sU"] - 6280) < 5 and abs(r["rho"] - 0.055) < 0.001
    assert abs(r["F_RUd"] - 6.83) < 0.01
    assert abs(r["dM"] - 12.6) < 0.1
    assert abs(r["dsig"] - 11.8) < 0.1
    assert abs(r["util"] - 0.68) < 0.01
    assert abs(r["d_sup"] - 2.69) < 0.01 and abs(r["d_span"] - 3.19) < 0.01 and abs(r["dM_req"] - 5.88) < 0.01
    assert r["ok"]


def test_app_runs():
    at = AppTest.from_file("app.py", default_timeout=60).run()
    assert not at.exception
    for opt in at.selectbox[1].options:          # paramètres de l'étude paramétrique
        at.selectbox[1].set_value(opt).run()
        assert not at.exception, opt
    for opt in at.selectbox[0].options:          # travée de référence
        at.selectbox[0].set_value(opt).run()
        assert not at.exception, opt
