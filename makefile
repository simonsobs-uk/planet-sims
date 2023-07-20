download:
	mkdir -p dist/bcp
	for file in initial_parameters LAT_f030_beam LAT_f040_beam LAT_f090_beam LAT_f150_beam LAT_f230_beam LAT_f290_beam SAT_f030_beam SAT_f040_beam SAT_f090_beam SAT_f150_beam SAT_f230_beam SAT_f290_beam SO_beam_models; do \
		wget https://github.com/simonsobs-uk/planet-sims/releases/latest/download/$$file.h5 -O dist/bcp/$$file.h5; \
	done
