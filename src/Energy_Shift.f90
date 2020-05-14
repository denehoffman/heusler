program EnergyMinimization
    implicit none
    character (16), dimension (:), allocatable :: configs
    character (64) :: enum_file, int_file
    character (5) :: buffer
    character (16) :: config, config_best
    integer, dimension (:), allocatable :: ids
    integer :: i, n, numlines = 0, header = 0, steps = 201, id_best
    real, dimension(4, 4, 2) :: intmatrix = 0
    real :: E = 0, E_best, j, k
    real, dimension (:), allocatable :: intvals

    call getarg(1, enum_file)
    call getarg(2, int_file)
    open(1, file=enum_file)
    do
        read(1, *, end=1001)
        numlines = numlines + 1
    end do
    1001 close(1)
    open(1, file=enum_file)
    do while(buffer /= 'start')
        read(1, *) buffer
        header = header + 1
    end do
    allocate(configs(numlines - header))
    allocate(ids(numlines - header))
    do n = 1, numlines - header
        read(1, *) ids(n), buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, buffer, buffer, buffer, buffer, &
            buffer, configs(n)
    end do
    close(1)
    allocate(intvals(steps))
    call linspace(intvals, 0.0, 2 * pi, steps)
    do i = 1, size(intvals)
        j = cos(intvals(i))
        k = sin(intvals(i))
        intmatrix(1, 1, 1) = j
        intmatrix(2, 2, 1) = j
        intmatrix(3, 3, 1) = j
        intmatrix(4, 4, 1) = j
        intmatrix(1, 1, 2) = k 
        intmatrix(2, 2, 2) = k 
        intmatrix(3, 3, 2) = k 
        intmatrix(4, 4, 2) = k 
        E_best = 0
        call getEnergy(configs(5), int_file, E_best, intmatrix)
        id_best = 5
        do n = 1, size(configs)
            config = configs(n)
            E = 0
            call getEnergy(config, int_file, E, intmatrix)
            if (E <= E_best) then
                E_best = E
                config_best = config
                id_best = ids(n)
            end if
        end do
        write(*, fmt="(f11.9, a1, f11.9, a1, i6)") j, ",", k, ",", id_best
    end do
    deallocate(intvals)
    deallocate(configs)
    deallocate(ids)
end program

subroutine getJK(config, int_file, J, K, intmatrix)
    implicit none
    character (64), intent(in) :: int_file
    character (16), intent(in) :: config
    real, intent(out) :: J, K
    integer :: posa, posb, dist, sa, sb
    real, dimension(4, 4, 2) :: intmatrix
    open(1, file=int_file)
    do
        read(1, *, end=1002) posa, posb, dist
        read(config(posa:posa), *) sa
        read(config(posb:posb), *) sb
        if (dist == 1) then
            J = J + intmatrix(sa, sb, dist)
        else
            K = K + intmatrix(sa, sb, dist)
        endif
    end do
    1002 close(1)

end subroutine
